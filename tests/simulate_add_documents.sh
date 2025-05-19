#!/bin/bash

# API Endpoint
API_URL="http://localhost:9001/api/v1/company/add_document"  

# Company ID
COMPANY_ID="company_123"

# JSON Payload
JSON_PAYLOAD=$(cat <<EOF
{
    "company_id": "$COMPANY_ID",
    "documents": [
        {
            "page_content": "Document 1: Introduction to AI.",
            "metadata": { "source": "AI Course", "author": "John Doe" },
            "id": "doc_001"
        },
        {
            "page_content": "Document 2: Deep Learning Basics.",
            "metadata": { "source": "AI Course", "author": "Jane Doe" },
            "id": "doc_002"
        },
        {
            "page_content": "Document 3: Natural Language Processing Overview.",
            "metadata": { "source": "AI Research", "author": "Dr. Smith" },
            "id": "doc_003"
        },
        {
            "page_content": "Document 4: Computer Vision and Image Recognition.",
            "metadata": { "source": "Machine Learning", "author": "Emily Clark" },
            "id": "doc_004"
        },
        {
            "page_content": "Document 5: Neural Networks Explained.",
            "metadata": { "source": "Deep Learning", "author": "Michael Brown" },
            "id": "doc_005"
        },
        {
            "page_content": "Document 6: Evolution of AI in Healthcare.",
            "metadata": { "source": "Medical AI", "author": "Dr. Watson" },
            "id": "doc_006"
        },
        {
            "page_content": "Document 7: AI in Finance - Use Cases.",
            "metadata": { "source": "Finance AI", "author": "Sarah Lee" },
            "id": "doc_007"
        },
        {
            "page_content": "Document 8: Ethical AI and Bias Reduction.",
            "metadata": { "source": "Ethics", "author": "John Ethics" },
            "id": "doc_008"
        },
        {
            "page_content": "Document 9: Generative AI Models like GPT.",
            "metadata": { "source": "AI Labs", "author": "Sam Wilson" },
            "id": "doc_009"
        },
        {
            "page_content": "Document 10: AI for Autonomous Vehicles.",
            "metadata": { "source": "Autonomous Cars", "author": "Elon Tech" },
            "id": "doc_010"
        },
        {
            "page_content": "Document 11: AI-powered Drug Discovery.",
            "metadata": { "source": "Pharmaceuticals", "author": "Dr. Alex" },
            "id": "doc_011"
        },
        {
            "page_content": "Document 12: Machine Learning in Cybersecurity.",
            "metadata": { "source": "Cybersecurity AI", "author": "Ethan Hunt" },
            "id": "doc_012"
        },
        {
            "page_content": "Document 13: AI-driven Personal Assistants.",
            "metadata": { "source": "Consumer AI", "author": "Siri Bot" },
            "id": "doc_013"
        },
        {
            "page_content": "Document 14: Speech Recognition Advances.",
            "metadata": { "source": "Voice Tech", "author": "Alexa" },
            "id": "doc_014"
        },
        {
            "page_content": "Document 15: AI and the Future of Work.",
            "metadata": { "source": "Workplace AI", "author": "HR Analytics" },
            "id": "doc_015"
        },
        {
            "page_content": "Document 16: Robotics and AI Synergy.",
            "metadata": { "source": "Robotics", "author": "Dr. Isaac" },
            "id": "doc_016"
        },
        {
            "page_content": "Document 17: AI in Smart Home Automation.",
            "metadata": { "source": "Smart Homes", "author": "Tech Review" },
            "id": "doc_017"
        },
        {
            "page_content": "Document 18: AI-powered Fraud Detection.",
            "metadata": { "source": "Banking AI", "author": "Fraud Analyst" },
            "id": "doc_018"
        },
        {
            "page_content": "Document 19: Quantum Computing and AI.",
            "metadata": { "source": "Quantum AI", "author": "Dr. Strange" },
            "id": "doc_019"
        },
        {
            "page_content": "Document 20: AI-driven Content Generation.",
            "metadata": { "source": "Content AI", "author": "GPT Model" },
            "id": "doc_020"
        },
        {
            "page_content": "Document 21: AI for Weather Prediction.",
            "metadata": { "source": "Climate AI", "author": "Meteorologist" },
            "id": "doc_021"
        },
        {
            "page_content": "Document 22: AI in Retail - Personalized Shopping.",
            "metadata": { "source": "E-commerce AI", "author": "Retail Analyst" },
            "id": "doc_022"
        },
        {
            "page_content": "Document 23: The Role of AI in Education.",
            "metadata": { "source": "EdTech", "author": "Prof. Learning" },
            "id": "doc_023"
        },
        {
            "page_content": "Document 24: AI-powered Chatbots in Customer Service.",
            "metadata": { "source": "Customer AI", "author": "Support Bot" },
            "id": "doc_024"
        },
        {
            "page_content": "Document 25: AI in Sports Analytics.",
            "metadata": { "source": "Sports AI", "author": "Game Analyst" },
            "id": "doc_025"
        }
    ],
    "data_type": "test"
}
EOF
)

# Sending Request
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

# Display Response
echo "Server Response: $RESPONSE"
