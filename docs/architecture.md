# VERIDEX System Architecture & Pipeline Specification

## Processing Flow

```
+------------------+
|   Input Image    |
+--------+---------+
         |
         v
+------------------+
|  Face Detection  |  (OpenCV YuNet)
+--------+---------+
         |
         v
+------------------+
|  Face Embedding  |  (OpenCV SFace)
+--------+---------+
         |
         v
+------------------+
|  Reverse Search  |  (SerpApi / Google Lens)
+--------+---------+
         |
         v
+------------------+
| Candidate Discovery| (Web & Social Media)
+--------+---------+
         |
         v
+------------------+
| Face Verification| (Cosine similarity against embedding)
+--------+---------+
         |
         v
+------------------+
| Evidence Scoring | (Cross-reference confidence & match ratio)
+--------+---------+
         |
         v
+------------------+
| Fingerprinting   | (Cryptographic evidence hash compilation)
+--------+---------+
         |
         v
+------------------+
| Blockchain Anchor| (Polygon Amoy Smart Contract)
+--------+---------+
         |
         v
+------------------+
| Integrity Check  | (On-chain vs submitted payload match & tamper detection)
+------------------+
```
