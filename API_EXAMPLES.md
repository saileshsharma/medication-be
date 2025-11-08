# API Usage Examples

Complete examples for integrating with the Pixel Pirates Backend API.

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://your-api.com/api/v1
```

## Authentication

Currently, the API doesn't require authentication. User identification is done via hashed user IDs for privacy.

## Examples

### 1. Analyze Text Content

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Breaking news: Climate summit reaches historic agreement",
    "content_type": "text",
    "source_app": "Twitter",
    "user_id_hash": "abc123xyz"
  }'
```

**JavaScript/TypeScript:**
```typescript
const analyzeContent = async (text: string) => {
  const response = await fetch('http://localhost:8000/api/v1/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content: text,
      content_type: 'text',
      source_app: 'Camera Scanner',
      user_id_hash: 'user123'
    })
  });

  const result = await response.json();
  return result;
};

// Usage
const result = await analyzeContent('Some news headline');
console.log(result.verdict); // VERIFIED, UNCLEAR, LIKELY_FAKE
console.log(result.credibility_score); // 0-100
```

**Python:**
```python
import requests

def analyze_content(text: str):
    url = "http://localhost:8000/api/v1/analyze"
    payload = {
        "content": text,
        "content_type": "text",
        "source_app": "Test Script",
        "user_id_hash": "user123"
    }

    response = requests.post(url, json=payload)
    return response.json()

# Usage
result = analyze_content("Climate change is affecting temperatures")
print(f"Verdict: {result['verdict']}")
print(f"Score: {result['credibility_score']}")
```

### 2. Get Scan History

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/history?user_id_hash=abc123&page=1&page_size=20"
```

**JavaScript:**
```javascript
const getHistory = async (userId, page = 1, pageSize = 20) => {
  const url = `http://localhost:8000/api/v1/history?user_id_hash=${userId}&page=${page}&page_size=${pageSize}`;
  const response = await fetch(url);
  const data = await response.json();

  console.log(`Total scans: ${data.total}`);
  data.scans.forEach(scan => {
    console.log(`${scan.verdict}: ${scan.content.substring(0, 50)}...`);
  });

  return data;
};
```

### 3. Get User Statistics

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/stats?user_id_hash=abc123&days=30"
```

**JavaScript:**
```javascript
const getStats = async (userId, days = 30) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/stats?user_id_hash=${userId}&days=${days}`
  );
  const stats = await response.json();

  console.log(`Total Scans: ${stats.total_scans}`);
  console.log(`Verified: ${stats.verified_count}`);
  console.log(`Fake: ${stats.fake_count}`);
  console.log(`Average Score: ${stats.average_credibility_score}`);

  return stats;
};
```

### 4. Submit Feedback

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/feedback?user_id_hash=abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "550e8400-e29b-41d4-a716-446655440000",
    "feedback_type": "disagree",
    "comment": "This is actually verified by Reuters"
  }'
```

**JavaScript:**
```javascript
const submitFeedback = async (scanId, feedbackType, comment) => {
  const response = await fetch(
    'http://localhost:8000/api/v1/feedback?user_id_hash=user123',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scan_id: scanId,
        feedback_type: feedbackType, // 'agree', 'disagree', 'report_error'
        comment: comment
      })
    }
  );

  return response.json();
};
```

### 5. Health Check

**cURL:**
```bash
curl http://localhost:8000/api/v1/health
```

**JavaScript:**
```javascript
const checkHealth = async () => {
  const response = await fetch('http://localhost:8000/api/v1/health');
  const health = await response.json();

  console.log(`Status: ${health.status}`);
  console.log(`Database: ${health.database}`);
  console.log(`Redis: ${health.redis}`);

  return health.status === 'healthy';
};
```

## React Native Integration

### Complete Example

```typescript
// api/analyzer.ts
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api/v1'
  : 'https://api.pixelpirates.com/api/v1';

export interface AnalysisResult {
  id: string;
  content: string;
  verdict: 'VERIFIED' | 'UNCLEAR' | 'LIKELY_FAKE' | 'CONFIRMED_FAKE';
  credibility_score: number;
  confidence: number;
  sources: Array<{
    name: string;
    url: string;
    credibility_rating: number;
  }>;
  explanation: {
    summary: string;
    reasons: string[];
  };
  processing_time_ms: number;
}

export const analyzeText = async (
  text: string,
  sourceApp: string = 'Camera Scanner',
  userId: string = 'anonymous'
): Promise<AnalysisResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: text,
        content_type: 'text',
        source_app: sourceApp,
        user_id_hash: userId
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
};

export const getUserStats = async (userId: string, days: number = 30) => {
  const response = await fetch(
    `${API_BASE_URL}/stats?user_id_hash=${userId}&days=${days}`
  );
  return response.json();
};

export const getScanHistory = async (
  userId: string,
  page: number = 1,
  pageSize: number = 20
) => {
  const response = await fetch(
    `${API_BASE_URL}/history?user_id_hash=${userId}&page=${page}&page_size=${pageSize}`
  );
  return response.json();
};
```

### Usage in Component

```typescript
// screens/CameraScannerScreen.tsx
import { analyzeText } from '../api/analyzer';

const handleScan = async (text: string) => {
  setLoading(true);

  try {
    const result = await analyzeText(text, 'Camera Scanner', userId);

    // Update UI with result
    setVerdict(result.verdict);
    setCredibilityScore(result.credibility_score);
    setSources(result.sources);
    setExplanation(result.explanation);

    // Add to local history
    addToHistory(result);

  } catch (error) {
    Alert.alert('Error', 'Failed to analyze content');
  } finally {
    setLoading(false);
  }
};
```

## Error Handling

```javascript
const analyzeWithErrorHandling = async (text) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: text, content_type: 'text' })
    });

    if (!response.ok) {
      if (response.status === 422) {
        throw new Error('Invalid request - check your input');
      } else if (response.status === 500) {
        throw new Error('Server error - please try again later');
      } else {
        throw new Error(`HTTP error ${response.status}`);
      }
    }

    return await response.json();

  } catch (error) {
    if (error.name === 'TypeError') {
      throw new Error('Network error - check your connection');
    }
    throw error;
  }
};
```

## Rate Limiting

The API has rate limits:
- 60 requests per minute
- 1000 requests per hour

Handle rate limit errors:

```javascript
const response = await fetch(url);

if (response.status === 429) {
  const retryAfter = response.headers.get('Retry-After');
  console.log(`Rate limited. Retry after ${retryAfter} seconds`);
  // Implement exponential backoff
}
```

## Caching

The backend caches results automatically. Identical content will return cached results with `cached: true`.

To bypass cache (not recommended):
```javascript
// Add timestamp to make content unique
const uniqueContent = `${text} [${Date.now()}]`;
```

## WebSocket Support (Coming Soon)

Real-time analysis updates will be available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analyze');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Analysis progress: ${update.progress}%`);
};

ws.send(JSON.stringify({ content: text }));
```

## Best Practices

1. **Always handle errors** - Network can be unreliable
2. **Show loading states** - Analysis takes 200-500ms
3. **Cache locally** - Don't re-analyze same content
4. **Respect rate limits** - Implement exponential backoff
5. **Use appropriate timeouts** - 10 seconds is reasonable
6. **Hash user IDs** - Never send raw user identifiers

---

Need help? Check the [interactive docs](http://localhost:8000/docs)
