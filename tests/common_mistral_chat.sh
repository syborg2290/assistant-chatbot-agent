#!/bin/bash

API_URL="http://localhost:9001/api/v1/ai/mistral-chat"  

# Company ID
COMPANY_ID="company_123"

# JSON request payload
JSON_PAYLOAD=$(cat <<EOF
{
    "company_id": "$COMPANY_ID",
    "user_id": "user_12345",
    "data_type": "test",
    "query": "Generate a compelling product description based on these reviews: 'Great battery life, sleek design, but a bit pricey.'",
    "user_instructions": "Make the description engaging and persuasive.",
    "k": 3,
    "metadata_filter": {
        "category": "electronics",
        "brand": "XYZ"
    },
    "search_type": "mmr",
    "temperature": 0.7,
    "top_k": 40,
    "top_p": 0.9,
    "num_gpu": 2
}
EOF
)

# Send request using curl
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

# Print response
echo "API Response:"
echo "$RESPONSE"
