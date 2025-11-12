# Client Node Schema - Detailed Example

## Sample Account: "AroundTown"

### Raw Salesforce Data
```json
{
  "Id": "0010800002m9v0DAAQ",
  "Name": "AroundTown",
  "Type": "Customer",
  "OwnerId": "00508000009YhZnAAK",
  "Owner": {
    "Name": "Amnon Sinai",
    "Email": "amnons@terasky.com.invalid"
  },
  "BillingCountry": "Germany",
  "BillingCity": "Berlin",
  "BillingState": null,
  "Phone": "+49-30-12345678",
  "Website": "https://aroundtown.de",
  "Description": "Real estate company based in Germany",
  "Industry_new__c": "Real Estate",
  "Sector__c": "Commercial",
  "Account_Status__c": "Active",
  "Account_Tier__c": "Tier 1",
  "Site__c": "EMEA",
  "Company_Size__c": "Enterprise",
  "Annual_Sales_Potential__c": "$500K+",
  "IsPartner": false,
  "Internal__c": false,
  "Test_Account__c": false,
  "Active_Contract__c": true,
  "Account_Manager_Cloud__c": "00508000009YhZpAAK",
  "CreatedDate": "2023-01-15T10:30:00.000Z",
  "LastModifiedDate": "2024-12-20T14:22:00.000Z"
}
```

---

## Neo4j Client Node Schema

```cypher
CREATE (:Client {
  // ============================================
  // CORE FIELDS (TSKB Standard)
  // ============================================
  name: "AroundTown",                          // Source: Account.Name
  source: "tskb-sf_api",                       // Source: Hardcoded (importer tag)
  
  // ============================================
  // SALESFORCE IDENTITY FIELDS
  // ============================================
  sf_id: "0010800002m9v0DAAQ",                 // Source: Account.Id
                                                // 🔑 SHARED KEY: Used for relationships
                                                // Links to: Opportunity.AccountId
  
  // ============================================
  // ACCOUNT CLASSIFICATION
  // ============================================
  sf_type: "Customer",                         // Source: Account.Type
                                                // Values: Customer, Prospect, Vendor, Partner, Other
  
  sf_industry: "Real Estate",                  // Source: Account.Industry_new__c
                                                // Custom field (replaces standard Industry)
  
  sf_sector: "Commercial",                     // Source: Account.Sector__c
                                                // Custom field for business sector
  
  sf_account_status: "Active",                 // Source: Account.Account_Status__c
                                                // Custom field for account status
  
  sf_account_tier: "Tier 1",                   // Source: Account.Account_Tier__c
                                                // Custom field for account priority/tier
  
  sf_site: "EMEA",                             // Source: Account.Site__c
                                                // Custom field for geographic site
  
  // ============================================
  // LOCATION FIELDS
  // ============================================
  sf_billing_country: "Germany",               // Source: Account.BillingCountry
                                                // 🔑 MAPPING KEY: Maps to Region node
                                                // Used for: Client→Region relationship
  
  // ============================================
  // CONTACT INFORMATION
  // ============================================
  sf_phone: "+49-30-12345678",                 // Source: Account.Phone
  
  sf_website: "https://aroundtown.de",         // Source: Account.Website
  
  sf_description: "Real estate company...",    // Source: Account.Description
  
  // ============================================
  // BUSINESS METRICS
  // ============================================
  sf_company_size: "Enterprise",               // Source: Account.Company_Size__c
                                                // Custom field for company size
  
  sf_annual_sales_potential: "$500K+",         // Source: Account.Annual_Sales_Potential__c
                                                // Custom field for sales potential
  
  // ============================================
  // ACCOUNT FLAGS
  // ============================================
  sf_is_partner: false,                        // Source: Account.IsPartner
                                                // Standard Salesforce field
  
  sf_active_contract: true,                    // Source: Account.Active_Contract__c
                                                // Custom field - active contract flag
  
  // ============================================
  // ACCOUNT MANAGER FIELDS (RELATIONSHIP KEYS)
  // ============================================
  sf_owner_id: "00508000009YhZnAAK",           // Source: Account.OwnerId
                                                // 🔑 SHARED KEY: Links to Employee.sf_id
                                                // Used for: Client→Employee (MANAGED_BY)
  
  sf_owner_name: "Amnon Sinai",                // Source: Account.Owner.Name
                                                // Denormalized for quick reference
  
  sf_owner_email: "amnons@terasky.com",        // Source: Account.Owner.Email (cleaned)
                                                // 🔑 SHARED KEY: Links to Employee.email
                                                // Note: Trimmed to @terasky.com domain only
                                                // Original: amnons@terasky.com.invalid
                                                // Used for: Email-based matching
  
  sf_account_manager_cloud_id: "00508000009YhZpAAK",  // Source: Account.Account_Manager_Cloud__c
                                                       // 🔑 SHARED KEY: Links to Employee.sf_id
                                                       // Used for: Client→Employee (CLOUD_MANAGED_BY)
  
  // ============================================
  // METADATA FIELDS
  // ============================================
  sf_created_date: datetime("2023-01-15T10:30:00.000Z"),     // Source: Account.CreatedDate
  
  sf_last_modified_date: datetime("2024-12-20T14:22:00.000Z"), // Source: Account.LastModifiedDate
  
  sf_synced_at: datetime("2025-01-15T16:45:00.000Z"),        // Source: Importer timestamp
  
  created_at: datetime("2025-01-15T16:45:00.000Z")            // Source: Importer timestamp
})
```

---

## Shared Keys & Relationships

### 🔑 Key Mapping Table

| Client Field | Links To | Target Node | Target Field | Relationship | Match Type |
|-------------|----------|-------------|--------------|--------------|------------|
| `sf_id` | Opportunity | Opportunity | `AccountId` | Future: USES→Product | Exact |
| `sf_owner_id` | Employee | Employee | `sf_id` | MANAGED_BY | Exact |
| `sf_owner_email` | Employee | Employee | `email` | MANAGED_BY | Email (cleaned) |
| `sf_account_manager_cloud_id` | Employee | Employee | `sf_id` | CLOUD_MANAGED_BY | Exact |
| `sf_billing_country` | Region | Region | `name` | LOCATED_IN | Mapping |

---

## Relationship Examples

### 1. Client→Employee (MANAGED_BY)

**Via sf_owner_id:**
```cypher
// Match by Salesforce User ID
MATCH (c:Client {sf_owner_id: "00508000009YhZnAAK"})
MATCH (e:Employee {sf_id: "00508000009YhZnAAK"})
CREATE (c)-[:MANAGED_BY]->(e)

// Result: AroundTown→Amnon Sinai
```

**Via sf_owner_email (fallback):**
```cypher
// Match by email (if sf_id not available)
MATCH (c:Client {sf_owner_email: "amnons@terasky.com"})
MATCH (e:Employee {email: "amnons@terasky.com"})
CREATE (c)-[:MANAGED_BY]->(e)

// Result: AroundTown→Amnon Sinai
```

### 2. Client→Employee (CLOUD_MANAGED_BY)

```cypher
// Match by Cloud Account Manager ID
MATCH (c:Client {sf_account_manager_cloud_id: "00508000009YhZpAAK"})
MATCH (e:Employee {sf_id: "00508000009YhZpAAK"})
CREATE (c)-[:CLOUD_MANAGED_BY]->(e)

// Result: AroundTown→[Cloud Account Manager]
```

### 3. Client→Region (LOCATED_IN)

```cypher
// Map Germany to closest region (or create mapping)
MATCH (c:Client {sf_billing_country: "Germany"})
MATCH (r:Region {name: "UK"})  // EMEA region mapping
CREATE (c)-[:LOCATED_IN]->(r)

// Result: AroundTown→UK (EMEA)
```

**Country→Region Mapping:**
```
Israel → IL
USA, United States → US
UK, United Kingdom, Germany, France, EMEA → UK
```

---

## Field Source Summary

### Standard Salesforce Fields (8)
- `Id`, `Name`, `Type`, `OwnerId`, `BillingCountry`
- `Phone`, `Website`, `Description`, `IsPartner`
- `CreatedDate`, `LastModifiedDate`

### Custom Salesforce Fields (9)
- `Industry_new__c` (replaces standard Industry)
- `Sector__c`, `Account_Status__c`, `Account_Tier__c`, `Site__c`
- `Company_Size__c`, `Annual_Sales_Potential__c`
- `Active_Contract__c`
- `Account_Manager_Cloud__c`

### Derived/Computed Fields (4)
- `source` → Hardcoded "tskb-sf_api"
- `sf_owner_name` → From Owner.Name
- `sf_owner_email` → From Owner.Email (trimmed to @terasky.com)
- `sf_synced_at` → Importer timestamp

### Total Fields: 21 properties

### Removed Fields (Not Needed):
- ❌ `BillingCity` - Not critical for relationships or queries
- ❌ `BillingState` - Not critical for relationships or queries
- ❌ `Internal__c` - Filtered out during import (Internal__c = false)
- ❌ `Test_Account__c` - Filtered out during import (Test_Account__c = false)

---

## Shared Key Analysis

### 🔑 Primary Keys (Unique Identifiers)
1. **sf_id** → Unique Salesforce Account ID
2. **name** → Account name (should be unique in practice)

### 🔗 Foreign Keys (Relationship Keys)
1. **sf_owner_id** → Links to Employee.sf_id (Salesforce User ID)
2. **sf_owner_email** → Links to Employee.email (email matching)
3. **sf_account_manager_cloud_id** → Links to Employee.sf_id (Cloud AM)
4. **sf_billing_country** → Maps to Region.name (via mapping table)

### 📊 Future Relationship Keys
1. **sf_id** → Will link to Opportunity.AccountId (for Client→Product via Opportunities)

---

## Comparison with Existing Nodes

### Employee Node Overlap
| Field | Client | Employee | Match Type |
|-------|--------|----------|------------|
| `sf_id` | Account.Id | User.Id | Different objects |
| `email` | sf_owner_email | email | ✅ Match for relationships |
| `name` | Account.Name | User.Name | Different context |
| `source` | tskb-sf_api | tskb-ms_api | Different sources |

### Region Node Overlap
| Field | Client | Region | Match Type |
|-------|--------|--------|------------|
| `sf_billing_country` | Germany, USA, Israel | - | Needs mapping |
| - | - | name (IL, US, UK) | ✅ Target for mapping |

### Product Node Overlap
| Field | Client | Product | Match Type |
|-------|--------|---------|------------|
| `sf_id` | Account.Id | Product2.Id | Different objects |
| Future: Opportunity link | ✅ Via Opportunity | ✅ Via OpportunityLineItem | Future relationship |

---

## Data Quality Notes

### ✅ Clean Data
- All required fields present
- Email format consistent with existing employees
- Country names standardized

### ⚠️ Considerations
- **BillingCountry**: Needs mapping to 3 regions (IL, US, UK)
- **Germany**: Not in current Region nodes → Map to UK (EMEA) or create new region
- **Email domain**: Trim to @terasky.com only (remove .invalid suffix)
- **Import filter**: Only import accounts with Account_Status__c = 'Active'

### 🔄 Relationship Matching Strategy
1. **Primary**: Match via `sf_owner_id` = `Employee.sf_id` (most reliable)
2. **Fallback**: Match via `sf_owner_email` = `Employee.email` (if sf_id missing)
3. **Cloud AM**: Match via `sf_account_manager_cloud_id` = `Employee.sf_id`

---

## Import Filters

### ✅ Accounts to Import
```python
WHERE Account_Status__c = 'Active'
  AND Internal__c = false
  AND Test_Account__c = false
  AND IsDeleted = false
```

### ❌ Accounts to Exclude
- Inactive accounts (Account_Status__c != 'Active')
- Internal accounts (Internal__c = true)
- Test accounts (Test_Account__c = true)
- Deleted accounts (IsDeleted = true)

---

## Email Cleaning Logic

```python
def clean_email(email):
    """
    Clean Salesforce email to @terasky.com domain only
    
    Examples:
    - amnons@terasky.com.invalid → amnons@terasky.com
    - ofirs@terasky.com.invalid → ofirs@terasky.com
    - admin@logicloud.co.il → None (not terasky domain)
    """
    if not email:
        return None
    
    # Extract username and domain
    if '@terasky.com' in email:
        # Split at @terasky.com and take everything before it
        username = email.split('@terasky.com')[0]
        return f"{username}@terasky.com"
    
    return None  # Not a terasky email
```

---

## Summary

**Total Properties**: 21 fields (reduced from 25)
**Shared Keys**: 4 relationship keys
**Relationships**: 3 types (MANAGED_BY, CLOUD_MANAGED_BY, LOCATED_IN)
**Data Source**: Salesforce Account object (filtered)
**Source Tag**: `tskb-sf_api`
**Import Filter**: Active accounts only
**Email Domain**: @terasky.com only
**Compatibility**: ✅ Aligns with existing Employee and Region schemas
