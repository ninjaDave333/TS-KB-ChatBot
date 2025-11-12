# Date Validation Rule

## Documentation Date Requirements

When updating any documentation files (CHANGELOG.md, ADR.md, ROADMAP.md, etc.) that include dates:

1. **ALWAYS ask the user for the current date** before adding or modifying any date entries
2. **NEVER assume or guess dates** - always verify with the user
3. **Use the exact date format**: YYYY-MM-DD
4. **Maintain chronological order** in changelogs and documentation

## Implementation Rule

Before modifying any file with date entries:
1. **Use executeBash tool to run `date` command** to get current system date
2. **Parse the output** to extract YYYY-MM-DD format
3. **Use the actual date** in documentation updates

## Examples

❌ **Wrong**: Assuming or guessing dates
✅ **Correct**: Run `executeBash` with `date` command, then use actual system date

This ensures all documentation reflects accurate implementation dates.