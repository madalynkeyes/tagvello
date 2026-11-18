# Project Brief: Smart Shopping & Price Tracking Mobile App

**Project status:** Planning / Pre-development  
**Project type:** Database-backed, cross-platform mobile application  
**Development timeline:** 3–5 weeks for an MVP  
**Target platforms:** iOS and Android  
**Working names:** WorthBuying, DealWatch, BasketBrain (final name TBD)

---

## 1. Project Overview

Build a mobile application that helps users make smarter purchasing decisions by tracking products they are interested in, monitoring prices over time, identifying worthwhile deals, and notifying users when products reach favorable prices.

The primary goal is to eliminate the need for users to repeatedly search retailer websites, compare prices manually, and check whether products have gone on sale.

Users should be able to find a product they want, save it to a personal watchlist, and let the application monitor it automatically.

Over time, the application should accumulate historical pricing data to provide insights into whether a product's current price represents a good deal.

The long-term vision is to create a personalized shopping intelligence platform that supports products from multiple retailers, automatically identifies relevant deals and offers, and helps users determine the best time and place to make a purchase.

**Core product philosophy:**

> Find it once. Track it automatically. Buy it when the price is right.

The application should be genuinely useful, easy to operate, and designed for continued use beyond the initial class project.

## 2. Problem Statement

Consumers frequently research products they want to purchase but are unsure whether the current price is a good deal.

Common frustrations include:

- Repeatedly checking websites to see whether a product has gone on sale.
- Forgetting about products they previously wanted to purchase.
- Missing limited-time promotions or price reductions.
- Not knowing whether a retailer's advertised discount is genuinely significant.
- Comparing prices manually across different retailers.
- Having no centralized location to track products they are considering purchasing.
- Spending excessive time deciding whether to buy immediately or wait for a better price.

Existing services such as Google Shopping, Keepa, and Honey address portions of this problem, but the proposed application aims to combine personal product tracking, historical price analysis, customizable alerts, and eventually cross-retailer comparison into one streamlined experience.

The product should emphasize personalized purchasing decisions rather than simply displaying advertisements or generic sales.

## 3. Target Users

The initial target users are everyday consumers who:

- Frequently research products before buying them.
- Prefer waiting for discounts rather than purchasing immediately.
- Want to track electronics, household products, clothing, appliances, and other consumer goods.
- Want notifications when specific products become affordable.
- Want to reduce unnecessary spending and repetitive shopping research.

The application should eventually support a wide variety of product categories.

For the MVP, supporting one retailer or a limited product category is acceptable if necessary to ensure reliability.

## 4. Primary User Experience

The ideal workflow is:

1. A user searches for a product in the mobile app or adds a supported product URL.
2. The app retrieves and displays available product information, including its name, image, retailer, and current observed price.
3. The user saves the product to their personal watchlist.
4. The user optionally specifies a target price or a minimum percentage discount.
5. The backend periodically retrieves updated pricing information from supported sources.
6. Each price observation is stored in the database with a timestamp.
7. The app evaluates whether the latest price satisfies the user's alert conditions.
8. When a meaningful price change occurs, the app sends a notification.
9. The user opens the app to review price history, understand the deal, and follow a link to the retailer.

The experience should require minimal manual effort after a product is saved.

### Example Scenario

A user wants to purchase wireless headphones currently priced at $329.

They add the headphones to their watchlist and specify a target price of $250.

Over the following weeks, the application records observed prices:

- Week 1: $329
- Week 2: $309
- Week 3: $279
- Week 4: $249

When the observed price reaches $249, the application sends a notification indicating that the product has reached the user's target price.

The user can open the product details page to view its observed price history and decide whether to purchase it.

These numbers are illustrative, not real product pricing data.

## 5. Core MVP Features

The following features should be prioritized for the initial 3–5 week development period.

### 5.1 Product Search and Discovery

Users can search for products using keywords.

The application retrieves products from at least one approved retailer or product-data API.

Each product should display available information such as:

- Product name
- Brand
- Model or product identifier
- Product image
- Current observed price
- Retailer
- Link to the retailer listing
- Last price-check timestamp

The application should distinguish unavailable, stale, and current pricing information.

### 5.2 Personal Watchlist

Users can save products they are interested in purchasing.

Watchlist functionality should include:

- Add a product.
- Remove a product.
- View all saved products.
- View the latest observed price.
- Configure alert preferences.
- Open detailed product information.

The watchlist should persist between sessions.

### 5.3 Historical Price Tracking

The backend periodically checks prices for monitored products.

Each observation should be stored with:

- Product listing identifier
- Observed price
- Currency
- Observation timestamp
- Data source
- Availability status, if provided

Historical observations should be retained even if the price has not changed.

This enables historical analysis and makes the database a central component of the application.

### 5.4 Price History Visualization

Users should be able to view a chart showing how a product's observed price has changed over time.

Potential statistics include:

- Latest observed price
- Lowest observed price
- Highest observed price
- Average observed price
- Percentage change over a selected period
- Time since the last successful price check

Statistics should be calculated from actual recorded observations, not invented historical values.

If insufficient data exists, the interface should clearly communicate that limitation.

### 5.5 Customizable Price Alerts

Users can configure conditions that trigger notifications.

Initial conditions:

- Price falls below a specified dollar amount.
- Price drops by a specified percentage.

Optional conditions:

- Price reaches its lowest observed value within a period.
- Product becomes available again.
- Price decreases by a meaningful amount compared with historical observations.

The system should prevent repeated notifications for the same unchanged condition.

Alert state and notification attempts should be persisted to support reliable delivery and debugging.

### 5.6 Automated Price Monitoring

A background process should periodically retrieve updated prices from supported sources.

Requirements:

- Operate without the mobile app being open.
- Avoid duplicate API requests when multiple users watch the same listing.
- Respect API rate limits and source usage terms.
- Handle failed requests gracefully.
- Record when each listing was last checked.
- Retry temporary failures where appropriate.
- Evaluate alerts after successful price updates.

A simple scheduled cloud worker is sufficient for the MVP.

### 5.7 Mobile Notifications

Users receive notifications when their configured alert conditions are met.

A notification should identify:

- The product
- The new observed price
- The condition that triggered the alert

Tapping the notification should open the relevant product details page when supported.

Push notifications are preferred, but an in-app notification feed or email alerts may be used as a fallback if needed.

### 5.8 Mobile Application

The application should have a polished, intuitive interface with a small number of core screens:

1. **Search:** Discover supported products.
2. **Watchlist:** View saved products and current prices.
3. **Product Details:** View price history and retailer information.
4. **Alert Settings:** Configure target prices and notification conditions.
5. **Settings:** Manage preferences and account information.

The design should prioritize simplicity and usefulness over feature quantity.

## 6. Potential Differentiating Features

The application should eventually offer more value than a basic price-drop tracker.

### 6.1 Deal Quality Analysis

Instead of relying on retailer-advertised discounts, analyze actual observed price history.

Potential insights:

- Current price compared with the historical average.
- Lowest observed price in the last 30 days.
- Percentage decrease from a recent observed price.
- Whether the current price is unusually low relative to available observations.

Example:

"This is the lowest price observed in the past 30 days."

Such statements must only be shown when sufficient data exists to support them.

The system should distinguish between retailer-advertised discounts and independently observed price changes.

### 6.2 Cross-Retailer Comparison

Eventually, users should be able to compare offers for the same product across multiple retailers.

For example:

| Retailer | Price | Shipping | Total |
|---|---:|---:|---:|
| Store A | $249 | $10 | $259 |
| Store B | $255 | Free | $255 |
| Store C | $269 | Free | $269 |

Illustrative prices only.

This requires accurate product matching, compatible currencies, and reliable information about shipping and other costs.

It should be treated as a post-MVP feature unless multiple reliable data sources are available early.

### 6.3 Intelligent Product Matching

Different retailers may describe identical products using different names.

The system could identify equivalent listings using:

- UPC or GTIN identifiers
- Manufacturer model numbers
- Brand and specifications
- Normalized product names
- AI-assisted similarity matching

AI should assist with ambiguous cases rather than replace deterministic identification.

Potential technologies include Gemini, embeddings, or other language-model APIs.

### 6.4 Deal and Promotion Tracking

Future versions could identify:

- Retailer promotions
- Coupons
- Seasonal discounts
- Limited-time offers
- Membership-exclusive prices
- Bundle deals

Offer conditions, expiration dates, eligibility requirements, and stacking restrictions should be modeled explicitly.

The application should not assume a promotion is applicable without sufficient information.

### 6.5 Easy Product Capture

Users could eventually save products through:

- Sharing a product link from a browser or shopping app.
- Pasting a URL.
- Scanning a product barcode.
- Uploading a product screenshot.
- Using a browser extension.

These features would reduce the effort required to maintain a watchlist.

Automatic monitoring of arbitrary browsing activity should not be assumed; users should explicitly choose what to save.

### 6.6 Shopping Basket Optimization

The original BasketBrain concept could eventually be incorporated.

Users create a shopping list, and the application determines where to purchase items at the lowest practical total cost.

Factors might include:

- Product prices
- Package sizes
- Availability
- Shipping
- Travel time
- Fuel costs
- Number of store visits

This is an advanced feature and should not be part of the initial MVP.

## 7. Recommended Technology Stack

The following stack is recommended but not mandatory. The development agent should evaluate alternatives where appropriate.

| Component | Recommended Technology | Purpose |
|---|---|---|
| Mobile frontend | React Native + Expo | Cross-platform iOS/Android app |
| Backend | Python + FastAPI | REST APIs and business logic |
| Database | PostgreSQL | Persistent relational and historical data |
| Managed database | Supabase | Hosted PostgreSQL and optional authentication |
| ORM | SQLAlchemy | Database access |
| Migrations | Alembic | Version-controlled schema changes |
| Scheduling | Cloud cron or scheduled worker | Automated price monitoring |
| Notifications | Expo Push Notifications | Price-drop alerts |
| Backend hosting | Railway or Render | Cloud deployment |
| Containerization | Docker | Consistent development and deployment |
| Testing | pytest | Backend and database testing |
| CI/CD | GitHub Actions | Automated tests and deployment workflows |
| Charts | React Native charting library | Price history visualization |
| AI (optional) | Gemini API | Product normalization and matching |

The goal is to learn mobile development, backend engineering, cloud deployment, and database design without introducing unnecessary architectural complexity.

Avoid microservices, Kubernetes, Kafka, or other infrastructure unless a concrete requirement justifies them.

## 8. Product Data Sources

**Data access is the project's most significant technical risk and must be validated before substantial development.**

Potential sources include:

### Best Buy Products API

A promising initial source for electronics.

Its developer documentation describes product information, pricing, availability, and product specifications.

Verify current access, permitted use, rate limits, and data-retention requirements.

Developer portal: https://developer.bestbuy.com/

### eBay Browse API

Supports searching listings and retrieving item information.

Potential limitations include production access requirements, listing condition differences, and restrictions on storing or redistributing data.

Documentation: https://developer.ebay.com/develop/api/buy/browse_api

### Amazon

Amazon's product-data APIs have access and program requirements that may complicate a short student project.

Do not make Amazon integration a dependency for the MVP.

### Other Retailers

Walmart, Target, and other retailers may be considered later, subject to available APIs, permissions, and usage terms.

### Important Data Principles

- Do not assume every retailer provides a usable public API.
- Do not rely on unauthorized or fragile scraping.
- Verify whether price history may legally be retained.
- Clearly distinguish live, stale, manually entered, and simulated data.
- Avoid claiming that observed prices represent the entire market.
- Do not fabricate historical prices.
- Use simulated price changes only for clearly labeled testing or demonstrations.

**Recommended strategy:** Begin with one permitted source, prove that repeated price collection works, and design the system to support additional source adapters later.

## 9. Proposed System Architecture

The application can follow a straightforward client-server architecture.

```text
                  MOBILE APPLICATION
                  React Native / Expo
                          |
                          | HTTPS / REST
                          v
                    FASTAPI BACKEND
                          |
            +-------------+-------------+
            |             |             |
            v             v             v
       Product API    Watchlist API   Alert API
            |             |             |
            +-------------+-------------+
                          |
                          v
                    POSTGRESQL
                          ^
                          |
                  PRICE INGESTION
                          ^
                          |
                  SCHEDULED WORKER
                          |
                          v
                  RETAILER API(S)


          After new price observations:
                          |
                          v
                   ALERT EVALUATION
                          |
                          v
                NOTIFICATION SERVICE
                          |
                          v
                     USER DEVICE
```

The mobile application should not directly expose retailer API keys or backend secrets.

The backend should be responsible for product retrieval, price processing, alert evaluation, and authorization.

Scheduled monitoring should run independently of mobile sessions.

## 10. Proposed Database Schema

The database should be normalized and designed to support multiple retailers, historical observations, and user-specific alert preferences.

### Core Tables

**users**
- id (primary key)
- email
- created_at

**products**
- id (primary key)
- name
- brand
- model_number
- gtin (nullable)
- category
- created_at

Represents a canonical product independent of a particular retailer.

**retailers**
- id (primary key)
- name
- website
- created_at

**listings**
- id (primary key)
- product_id (foreign key)
- retailer_id (foreign key)
- external_product_id
- url
- item_condition
- currency
- last_checked_at
- availability_status

Represents a retailer-specific listing for a product.

**price_observations**
- id (primary key)
- listing_id (foreign key)
- price
- currency
- observed_at
- source
- availability_status

Stores timestamped pricing observations.

**watchlist_items**
- id (primary key)
- user_id (foreign key)
- product_id (foreign key)
- created_at
- active

Stores products saved by users.

**alert_rules**
- id (primary key)
- watchlist_item_id (foreign key)
- target_price
- minimum_drop_percent
- cooldown_hours
- enabled
- created_at

Stores user-defined notification conditions.

**notification_events**
- id (primary key)
- alert_rule_id (foreign key)
- listing_id (foreign key)
- triggering_observation_id (foreign key)
- status
- created_at
- sent_at

Tracks alert creation and delivery state.

**device_tokens**
- id (primary key)
- user_id (foreign key)
- push_token
- platform
- updated_at

Stores push-notification destinations.

### Database Design Considerations

- Use foreign keys to enforce relationships.
- Use decimal/numeric types rather than floating-point for money.
- Store timestamps in UTC.
- Use appropriate uniqueness constraints for retailer identifiers and user watchlists.
- Index price observations by listing and observation timestamp.
- Design price-history queries to avoid unnecessary full-table scans.
- Use database transactions for alert creation.
- Prevent duplicate alerts through state tracking and idempotency constraints.
- Consider how to handle deleted products and inactive listings.
- Keep canonical products separate from retailer-specific listings.
- Plan for currencies, product variants, and item condition differences.
- Authenticate users and authorize access to their watchlists and notifications.

## 11. Interesting Database and Backend Problems

This project should demonstrate more than basic CRUD functionality.

Potential engineering challenges include:

**Historical analytics**

Use SQL aggregations and window functions to calculate price changes, rolling averages, and observed minimum prices.

**Efficient monitoring**

If 100 users track the same listing, the backend should retrieve its price once per monitoring interval rather than making 100 identical external requests.

**Reliable alerts**

A scheduled worker may crash, retry, or process the same observation twice. The system should prevent duplicate logical alerts.

**Product identity**

Different listings may refer to the same product. Product normalization and matching must account for identifiers, specifications, and variants.

**Data freshness**

Price observations should retain timestamps so the interface can communicate when prices were last verified.

**Performance**

Create indexes and evaluate query plans for common queries such as retrieving the latest observed price for every watchlist item.

**Background processing**

Separate scheduled ingestion from user-facing API requests to keep the application responsive.

## 12. Development Roadmap

### Week 1 — Technical Validation and Database Foundation

Goals:
- Verify access to a permitted product-pricing API.
- Retrieve real product identifiers and prices.
- Design and create the PostgreSQL schema.
- Implement a basic price-ingestion script.
- Store repeated observations.
- Establish the project repository and development environment.

**Milestone:** Successfully retrieve and persist prices for at least 10 real products.

### Week 2 — Backend Development

Goals:
- Create FastAPI endpoints.
- Implement product search.
- Implement watchlist operations.
- Implement price-history retrieval.
- Implement alert-rule management.
- Add automated backend tests.
- Add authentication if appropriate.

**Milestone:** All core operations work through the backend API.

### Week 3 — Mobile Application

Goals:
- Initialize React Native / Expo.
- Build product search.
- Build the personal watchlist.
- Build product details.
- Display historical price charts.
- Allow users to configure alert thresholds.
- Connect the mobile app to the backend.

**Milestone:** The complete product-tracking workflow works on a phone.

### Week 4 — Automation and Deployment

Goals:
- Deploy the backend.
- Configure scheduled price monitoring.
- Implement price-change detection.
- Evaluate alert rules.
- Send notifications.
- Add logging, retries, and duplicate-alert prevention.
- Test end-to-end behavior.

**Milestone:** A test price change produces an appropriate notification without the app being open.

### Week 5 — Polish and Stretch Features

Goals:
- Improve interface design.
- Handle missing or stale data.
- Improve error messages.
- Add monitoring and basic observability.
- Optimize database queries.
- Create an installable test build.
- Prepare a demonstration and documentation.

Potential stretch features:
- Deal-quality scoring.
- Cross-retailer comparison.
- Product URL import.
- Barcode scanning.
- AI-assisted product matching.

**Milestone:** Another user can install and successfully test the application.

## 13. MVP Success Criteria

The project should be considered successful if:

1. A user can discover a product from at least one supported source.
2. The user can save that product to a persistent watchlist.
3. The backend can automatically collect and store updated prices.
4. The app displays genuine historical observations.
5. The user can define a price-alert condition.
6. The system detects when that condition is satisfied.
7. The user receives a notification or reliable in-app alert.
8. The application and backend run in a deployed environment.
9. The core experience can be demonstrated on a real phone.
10. The database design and query logic can be explained and tested.

The application does not need to support every retailer or product category to satisfy these requirements.

## 14. Important Risks and Constraints

### API Availability

Retailer APIs may have approval requirements, usage restrictions, or rate limits.

**Mitigation:** Validate access immediately and isolate retailer integrations behind a provider interface.

### Historical Data Availability

A new system will not initially have months of historical prices.

**Mitigation:** Accumulate genuine observations over time and use labeled synthetic data for demonstrations and tests.

### Product Matching

Different products may have similar names, and identical products may have different retailer descriptions.

**Mitigation:** Prioritize exact identifiers and explicit model attributes before AI-assisted matching.

### Alert Reliability

Background jobs and notification providers can fail.

**Mitigation:** Persist alert state, log failures, retry safely, and prevent duplicate logical notifications.

### Scope Creep

Cross-retailer comparison, coupon tracking, barcode scanning, AI recommendations, and grocery basket optimization could greatly expand development time.

**Mitigation:** Complete the core tracking-and-alert workflow before implementing stretch features.

### Mobile Distribution

Public App Store and Google Play publication may require developer accounts, review, and compliance work.

**Mitigation:** Prioritize installable test builds. Treat public store publication as a separate milestone.

### Privacy and Security

Users may store personal shopping preferences and device notification tokens.

**Mitigation:** Use secure authentication, HTTPS, appropriate database access controls, protected secrets, and minimal collection of personal information.

## 15. Potential Future Roadmap

After the MVP, the application could expand into a broader shopping intelligence platform.

**Phase 2: Better product tracking**
- Multiple retailers
- Shared product identities
- More advanced price analysis
- URL sharing
- Barcode scanning

**Phase 3: Intelligent purchasing**
- Deal-quality scores
- Personalized recommendations
- Coupon and promotion tracking
- AI-assisted product matching
- Price prediction with uncertainty estimates

**Phase 4: Shopping optimization**
- Grocery and household shopping lists
- Package-size and unit-price comparison
- Multi-store basket optimization
- Travel and shipping cost calculations
- Shared household watchlists

These are future possibilities, not MVP commitments.

## 16. Portfolio and Recruiter Goals

This is also a software engineering portfolio project.

The implementation should demonstrate:

- Relational database design and normalization
- SQL query optimization
- Backend API development
- Third-party API integration
- Background job scheduling
- Event-driven notifications
- Cloud deployment
- Cross-platform mobile development
- Automated testing
- Secure application design
- Practical system architecture decisions

Potential measurable achievements include:

- Number of products monitored
- Number of price observations processed
- Average query response time
- Time between detecting a qualifying price change and creating an alert
- Duplicate-alert prevention accuracy
- Number of successful scheduled monitoring runs

A polished README should document the architecture, database schema, key design decisions, setup instructions, testing strategy, and known limitations.

The finished project should have a short demonstration video showing a user saving a product, viewing historical prices, setting an alert, and receiving a notification.

## 17. Instructions for the AI Development Agent

You are helping plan and implement this project.

**Do not immediately generate the entire application.**

Begin by reviewing this specification and helping make the remaining architectural and product decisions.

Prioritize:

1. Validating the availability and permitted use of real product-pricing data.
2. Defining a small, achievable MVP.
3. Selecting an appropriate technology stack.
4. Designing a normalized relational database schema.
5. Planning the backend and mobile application architecture.
6. Breaking development into small, testable milestones.
7. Identifying risks before committing to complex integrations.

When making technical recommendations:

- Explain important tradeoffs.
- Prefer simple, maintainable solutions.
- Avoid unnecessary infrastructure.
- Distinguish required features from optional enhancements.
- Do not assume access to external APIs without verification.
- Do not fabricate product prices or historical data.
- Treat AI as an optional enhancement, not a mandatory dependency.
- Favor production-relevant engineering practices that are achievable within the timeline.
- Keep the application useful to real users, not merely impressive as a demonstration.

The project is still in the planning stage. The exact product name, final feature set, retailer integrations, and architecture have not been finalized.

**First task:** Evaluate the proposed MVP, identify any critical unknowns or blockers, recommend a practical architecture, and propose the first concrete development milestone.

---

## Final Product Vision

Build a useful, deployable mobile application that remembers products users want to buy, monitors their prices, identifies meaningful deals, and notifies users when purchasing conditions are favorable.

The initial version should deliver a reliable, polished personal price-tracking experience.

The long-term vision is a broader shopping intelligence platform that helps users answer:

**"Is this actually a good deal, and is now the right time to buy it?"**
