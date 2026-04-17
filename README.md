## Project Overview
The core of VibeTube lies in its relational database design, ensuring that interactions from video uploads to user subscriptions—are tracked with precision. The application utilizes a custom UI to interact with the underlying data, making complex SQL operations accessible through an intuitive interface.

## Core Features
Dual-Role User System: Comprehensive management for Creators (content management, upload history) and Viewers (watch lists, interactions).

Relational Video Mapping: A dedicated video table that links content to creators, categories, and performance metrics.

Interactive Database Schema: Optimized for 3rd Normal Form (3NF) to reduce redundancy and ensure data consistency.

Search & Filter: SQL-driven search functionality to query specific creators or video metadata.

## Database Schema & Architecture
The system is built on a relational model that defines the lifecycle of a video and its relationship to the user base.

Key Entities:
Users: Stores credentials, profile data, and role identifiers (Creator vs. Viewer).

Videos: Contains metadata including titles, descriptions, and foreign keys linking back to the Creator.

Interactions: Handles the many-to-many relationships between users and content (e.g: likes, comments, and subscriptions).
