# Data Storage Architecture

## Overview

Your Pixel Pirates backend uses two storage systems:
- **PostgreSQL** - Permanent storage of all scan results and analytics
- **Redis** - Temporary cache for faster repeat queries

---

## 🗄️ PostgreSQL Database

### What's Stored Permanently:

PostgreSQL stores **all scan results and historical data** for analytics and improvement.

### Database Tables:

#### 1. **scan_results** (Main Table)
Stores every content scan performed by users.

**Data Stored:**
- `id` - Unique scan ID (UUID)
- `content` - The actual text that was scanned
- `content_type` - Type (text, url, image)
- `content_hash` - SHA256 hash of content (for deduplication)
- **Analysis Results:**
  - `verdict` - VERIFIED, UNCLEAR, LIKELY_FAKE, or CONFIRMED_FAKE
  - `credibility_score` - 0-100 score
  - `confidence` - 0.0-1.0 confidence level
- **Metadata:**
  - `timestamp` - When scan was performed
  - `source_app` - Where scan came from (Camera Scanner, URL Scanner, etc.)
  - `processing_tier` - Which AI tier processed it (1=device, 2=edge, 3=cloud)
  - `processing_time_ms` - How long analysis took
- **Explanation:**
  - `explanation_summary` - Human-readable explanation
  - `explanation_reasons` - Array of specific reasons (JSON)
  - `counter_evidence` - Alternative viewpoints (JSON)
- **Sources:**
  - `sources` - Array of fact-checking sources used (JSON)
- **Privacy & Analytics:**
  - `user_id_hash` - **Hashed user ID** (NOT the actual user ID - privacy preserved)
  - `cached` - Whether result came from cache

**Example Row:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Breaking news: New study shows...",
  "verdict": "UNCLEAR",
  "credibility_score": 67,
  "confidence": 0.72,
  "timestamp": "2025-01-08T10:30:00Z",
  "user_id_hash": "a3f5e8d9c4b2...",  // Hashed, not real user ID
  "sources": [
    {"name": "Reuters", "url": "...", "credibility": 0.95}
  ]
}
```

---

#### 2. **source_credibility**
Stores credibility ratings for news sources/domains.

**Data Stored:**
- `domain` - Website domain (e.g., "reuters.com")
- `credibility_score` - 0.0-1.0 rating
- `bias_rating` - Political bias (left, center, right)
- `fact_check_record` - Historical accuracy (JSON)
- `last_updated` - When rating was last updated

**Example:**
```json
{
  "domain": "reuters.com",
  "credibility_score": 0.95,
  "bias_rating": "center",
  "fact_check_record": {"accurate": 950, "false": 5}
}
```

---

#### 3. **known_fakes**
Registry of confirmed fake/misleading content.

**Data Stored:**
- `id` - Unique ID
- `content_hash` - Hash of the fake content
- `content_type` - Type of content
- `verified_fake` - Confirmed as fake (boolean)
- `source_fact_checker` - Who verified it (e.g., "Snopes")
- `report_count` - How many times reported
- `added_at` - When added to registry

**Purpose:** Fast lookup for known fake news - instant "CONFIRMED_FAKE" verdict

---

#### 4. **user_feedback**
User feedback on scan accuracy.

**Data Stored:**
- `id` - Unique feedback ID
- `scan_id` - Which scan this feedback is for
- `user_id_hash` - **Hashed user ID** (privacy preserved)
- `feedback_type` - agree, disagree, report_error
- `comment` - Optional user comment
- `created_at` - When feedback was given

**Purpose:** Improve AI accuracy over time

---

## ⚡ Redis Cache

### What's Cached Temporarily:

Redis stores **recently scanned content** for fast repeat lookups.

### Cache Strategy:

#### 1. **Scan Results Cache**
**Key Format:** `scan:{content_hash}`

**Data Cached:**
```json
{
  "id": "uuid",
  "verdict": "UNCLEAR",
  "credibility_score": 67,
  "confidence": 0.72,
  "explanation": {...},
  "sources": [...],
  "cached": true
}
```

**TTL (Time To Live):** 1 hour (3600 seconds)

**Why Cache:**
- Same content scanned multiple times → instant response
- Reduces API calls to fact-checking services
- Saves processing time and costs

**Example Use Case:**
1. User A scans: "Breaking: XYZ happened" → Full analysis (2 seconds)
2. User B scans same text 10 minutes later → Cached result (50ms)
3. After 1 hour → Cache expires, next scan does full analysis again

---

## 🔒 Privacy & Security

### User Privacy:

**User IDs are NEVER stored directly:**
- ✅ Stored: `SHA256(user_id)` = `a3f5e8d9c4b2...`
- ❌ NOT stored: Actual user ID or email

**Why Hash?**
- Allows analytics (same user scanning multiple times)
- Prevents identifying individual users
- One-way encryption (can't reverse to get user ID)

**Content Storage:**
- ✅ Scanned text is stored (needed for accuracy improvement)
- ✅ You can add content deletion/retention policies later
- ❌ No personal user information stored

---

## 📊 Data Usage

### What This Data Enables:

#### PostgreSQL (Permanent):
1. **User History** - "Show my past scans"
2. **Statistics** - "Scans this week: 42"
3. **Analytics** - Improve AI accuracy
4. **Known Fakes** - Instant detection of viral misinformation
5. **Source Ratings** - Learn which sources are credible

#### Redis (Temporary):
1. **Speed** - Instant results for popular content
2. **Cost Savings** - Reduce API calls
3. **Performance** - Handle traffic spikes

---

## 🔢 Data Size Estimates

### PostgreSQL Storage:

**Per Scan:**
- Text content: ~500 bytes (average)
- Metadata: ~200 bytes
- Analysis results: ~300 bytes
- **Total per scan: ~1 KB**

**Scale:**
- 1,000 scans = 1 MB
- 1,000,000 scans = 1 GB
- 10,000,000 scans = 10 GB

**Railway Free Tier:** 100 MB - 1 GB (enough for 100,000 - 1,000,000 scans)

### Redis Cache:

**Per Cached Scan:** ~1 KB

**With 1 hour TTL:**
- Light traffic: 10-100 items cached (~100 KB)
- Medium traffic: 1,000 items (~1 MB)
- Heavy traffic: 10,000 items (~10 MB)

**Railway Free Tier:** 100 MB Redis (more than enough)

---

## 🗑️ Data Retention

### Current Settings:

**PostgreSQL:**
- ✅ Stored permanently
- ⚠️ You may want to add cleanup policies later:
  - Delete scans older than 1 year
  - Archive old data

**Redis:**
- ✅ Auto-expires after 1 hour
- ✅ No manual cleanup needed
- ✅ Automatically handles memory limits

---

## 🔍 Sample Queries

### What Users Can See:

1. **My Scan History:**
   ```sql
   SELECT * FROM scan_results
   WHERE user_id_hash = 'user_hash_here'
   ORDER BY timestamp DESC
   LIMIT 50
   ```

2. **My Stats (Last 7 Days):**
   ```sql
   SELECT
     COUNT(*) as total_scans,
     AVG(credibility_score) as avg_score,
     SUM(CASE WHEN verdict = 'CONFIRMED_FAKE' THEN 1 ELSE 0 END) as fakes_caught
   FROM scan_results
   WHERE user_id_hash = 'user_hash_here'
     AND timestamp > NOW() - INTERVAL '7 days'
   ```

3. **Check if Content Was Scanned Before:**
   ```sql
   SELECT * FROM scan_results
   WHERE content_hash = 'hash_here'
   LIMIT 1
   ```

---

## 🎯 Key Takeaways

### PostgreSQL Stores:
✅ Every scan result (permanent)
✅ Known fake content registry
✅ Source credibility ratings
✅ User feedback
✅ **Privacy-preserving:** Only hashed user IDs

### Redis Caches:
✅ Recent scan results (1 hour)
✅ Frequently scanned content
✅ Automatic expiration
✅ No permanent storage

### Privacy:
✅ User IDs are hashed (one-way encryption)
✅ No personal information stored
✅ Content is stored (for accuracy improvement)
✅ You own all data on Railway

---

## 💡 Optional Future Enhancements

Consider adding:
1. **Data Retention Policy** - Auto-delete scans older than X months
2. **User Data Export** - GDPR compliance
3. **Content Deletion** - Allow users to delete their scan history
4. **Anonymization** - Further anonymize old scans
5. **Backup Strategy** - Regular database backups

---

**Questions?** All data is stored securely on Railway's infrastructure with industry-standard encryption.
