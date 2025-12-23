# User Feedback System

## Overview
User feedback system allowing users to rate answers with thumbs up/down, tracking satisfaction and identifying improvement areas.

## Implementation Date
December 22, 2025

## Components

### Frontend (promptui.html)
**Feedback Buttons**:
- 👍 Helpful / 👎 Not Helpful buttons on every bot response
- Buttons disable after click and highlight selected feedback
- Visual feedback: Green for positive, red for negative

**Data Sent**:
```javascript
{
  query: "user's question",
  answer: "bot's response",
  feedback: "positive" | "negative",
  metadata: {
    method: "ai_generated",
    dataCount: 5,
    executionTime: 2.3
  },
  user: "user@example.com",
  timestamp: "2025-12-22T14:30:00Z"
}
```

### Backend API

#### POST /api/v1/feedback
Records user feedback for answers.

**Request**:
```json
{
  "query": "Which HashiCorp products were purchased in 2025?",
  "answer": "Based on the purchase data...",
  "feedback": "positive",
  "metadata": {
    "method": "ai_generated",
    "dataCount": 5,
    "executionTime": 2.3
  },
  "user": "user@example.com",
  "timestamp": "2025-12-22T14:30:00Z"
}
```

**Response**:
```json
{
  "status": "feedback_recorded"
}
```

**Storage**: `/home/ubuntu/meetingsBotLogs/persistentData/user_feedback.jsonl`
- One JSON line per feedback entry
- Append-only for data integrity

#### GET /api/v1/feedback/analytics
Returns aggregated feedback analytics.

**Response**:
```json
{
  "total_feedback": 42,
  "positive": 38,
  "negative": 4,
  "satisfaction_rate": 90.5,
  "by_intent": {
    "sales_v1": {"positive": 15, "negative": 1},
    "calendar_v1": {"positive": 12, "negative": 0},
    "product_v1": {"positive": 8, "negative": 2},
    "strict_v1": {"positive": 3, "negative": 1}
  }
}
```

### Dashboard Integration
**Production Dashboard** (`/promptui/dashboard.html`):
- Displays **User Satisfaction %** as KPI card
- Auto-refreshes every 10 seconds
- Shows satisfaction rate alongside query count, response time, and error rate

### Analytics Script
**analyze_feedback.py**:
```bash
python Tests/analyze_feedback.py
```

**Output**:
```json
{
  "total_feedback": 42,
  "positive": 38,
  "negative": 4,
  "satisfaction_rate": 90.5,
  "by_intent": {...},
  "by_user": {
    "user1@example.com": {"positive": 10, "negative": 1},
    "user2@example.com": {"positive": 8, "negative": 0}
  },
  "recent": [
    {
      "query": "Which clients closed the most deals...",
      "feedback": "positive",
      "user": "user@example.com",
      "timestamp": "2025-12-22T14:30:00Z"
    }
  ]
}
```

## Use Cases

### 1. Track Overall Satisfaction
Monitor satisfaction rate over time to measure system quality improvements.

### 2. Identify Problem Intents
Find which query types (sales, calendar, product, strict) get negative feedback most often.

### 3. User-Specific Analysis
Identify power users and their satisfaction levels.

### 4. Continuous Improvement
Use negative feedback to:
- Identify failing query patterns
- Improve intent classification
- Enhance answer generation
- Add missing keywords

## Metrics

### Key Performance Indicators
- **Satisfaction Rate**: % of positive feedback (target: >90%)
- **Total Feedback**: Number of user ratings
- **Feedback by Intent**: Satisfaction breakdown by query type
- **Feedback by User**: User engagement and satisfaction

### Dashboard Display
```
┌─────────────────────────────────────────┐
│ User Satisfaction: 90.5%                │
│ (38 positive, 4 negative out of 42)    │
└─────────────────────────────────────────┘
```

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic thumbs up/down feedback
- ✅ Feedback storage in JSONL
- ✅ Analytics endpoint
- ✅ Dashboard integration

### Phase 2 (Planned)
- [ ] Feedback comments/reasons
- [ ] Feedback trends over time chart
- [ ] Email alerts for low satisfaction
- [ ] Automatic retraining triggers

### Phase 3 (Future)
- [ ] ML-based feedback analysis
- [ ] Predictive satisfaction scoring
- [ ] A/B testing for answer variations
- [ ] User feedback clustering

## Data Privacy
- User email stored with consent (authenticated users)
- No PII in queries/answers (sanitized)
- JSONL format allows easy GDPR compliance (delete specific lines)
- Data retention: 90 days (configurable)

## Monitoring
- Check feedback file size: `ls -lh /home/ubuntu/meetingsBotLogs/persistentData/user_feedback.jsonl`
- Monitor satisfaction rate in dashboard
- Run analytics script weekly for trends
- Alert if satisfaction drops below 80%
