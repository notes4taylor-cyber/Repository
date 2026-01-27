# Card Show Vendor

A trading card vendor simulation game built for Unreal Engine 5.3.

## Game Overview

Work your way up the ladder as a vendor at trading card shows! Start as a small-time dealer at local shows and build your empire to become an elite vendor at the biggest conventions.

## Features

### Card System
- **Multiple Card Types**: Baseball, Basketball, Football, Pokemon, Magic: The Gathering, and more
- **Rarity System**: Common, Uncommon, Rare, Ultra Rare, Legendary, and 1/1 cards
- **Card Conditions**: From Poor to Gem Mint with value multipliers
- **Professional Grading**: PSA, BGS, CGC grading simulation
- **Market Values**: Dynamic pricing based on market conditions

### Progression System
- **6 Vendor Tiers**: Beginner → Amateur → Established → Professional → Expert → Elite
- **Reputation System**: Earn rep from sales, customer service, and show attendance
- **Achievements**: Unlock rewards for milestones
- **Feature Unlocks**: Better booths, more display cases, premium shows

### Card Shows
- **Multiple Show Types**: Local, Regional, National, and Premium Showcase events
- **Dynamic Customer AI**: Different customer types with varying budgets and preferences
- **Real-time Trading**: Negotiate prices with customers
- **Show Statistics**: Track sales, revenue, and performance

### Economy System
- **Dynamic Market**: Prices fluctuate based on trends and events
- **Market Events**: Random events affect card values
- **Pack Opening**: Buy and open card packs to build inventory
- **Buy/Sell Trading**: Purchase cards from other vendors

### Customer Types
- **Casual Collectors**: Low budget, impulse buyers
- **Dedicated Collectors**: Looking for specific cards
- **Investors**: Seeking undervalued cards
- **Flippers**: Only buy deals they can resell
- **Whales**: High budget, premium buyers
- **Newbies**: New to collecting, need guidance

## Project Structure

```
CardShowVendor/
├── Source/CardShowVendor/
│   ├── Core/           # GameMode, PlayerController, PlayerState
│   ├── Cards/          # Card data, instances, database
│   ├── Booth/          # Vendor booth management
│   ├── Shows/          # Card show events
│   ├── Customers/      # Customer AI and behavior
│   ├── Economy/        # Market and progression systems
│   └── UI/             # HUD and widget classes
├── Config/             # Engine and game configuration
└── Content/            # Assets, blueprints, maps
```

## Getting Started

1. Open the project in Unreal Engine 5.3
2. Build the project (Development configuration)
3. Create a new map or use the provided starter map
4. Set the GameMode to `CSVGameMode`
5. Play in editor or package for your target platform

## Key Classes

| Class | Description |
|-------|-------------|
| `ACSVGameMode` | Main game mode managing subsystems |
| `ACSVPlayerController` | Player input and UI management |
| `ACSVPlayerState` | Player data, inventory, money |
| `UCSVCardDatabase` | Card definitions and pack configurations |
| `UCSVCardInstance` | Individual card instances with conditions |
| `ACSVVendorBooth` | Player's booth with display cases |
| `ACSVCardShow` | Card show event management |
| `ACSVCustomer` | Customer AI with buying behavior |
| `UCSVEconomyManager` | Market prices and trends |
| `UCSVProgressionManager` | Levels, tiers, achievements |

## Customization

### Adding New Cards
Create new `UCSVCardData` assets or add cards programmatically in `CSVCardDatabase::GenerateDefaultCards()`.

### Modifying Shows
Edit `CSVCardShow::InitializeShowPresets()` to add or modify show configurations.

### Customer Behavior
Adjust customer parameters in `CSVCustomer::SetCustomerTypeDefaults()`.

## License

Copyright Card Show Vendor. All Rights Reserved.
