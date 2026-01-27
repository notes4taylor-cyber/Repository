// Copyright Card Show Vendor. All Rights Reserved.

#include "Customers/CSVCustomer.h"
#include "Booth/CSVVendorBooth.h"
#include "Cards/CSVCardInstance.h"
#include "CardShowVendor.h"

ACSVCustomer::ACSVCustomer()
{
	PrimaryActorTick.bCanEverTick = true;

	CustomerType = ECSVCustomerType::Casual;
	CurrentState = ECSVCustomerState::Wandering;
	Budget = 50.0f;
	Patience = 60.0f;
	HaggleSkill = 0.5f;
	KnowledgeLevel = 0.5f;

	BrowseTimer = 0.0f;
	PatienceTimer = 0.0f;
	CardsExamined = 0;
	OffersRejected = 0;

	TargetBooth = nullptr;
}

void ACSVCustomer::BeginPlay()
{
	Super::BeginPlay();
}

void ACSVCustomer::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	UpdateBehavior(DeltaTime);
}

void ACSVCustomer::InitializeCustomer(float WealthMultiplier)
{
	// Random customer type weighted towards common types
	float TypeRoll = FMath::FRand();
	if (TypeRoll < 0.35f)
	{
		CustomerType = ECSVCustomerType::Casual;
	}
	else if (TypeRoll < 0.55f)
	{
		CustomerType = ECSVCustomerType::Dedicated;
	}
	else if (TypeRoll < 0.70f)
	{
		CustomerType = ECSVCustomerType::Newbie;
	}
	else if (TypeRoll < 0.82f)
	{
		CustomerType = ECSVCustomerType::Flipper;
	}
	else if (TypeRoll < 0.92f)
	{
		CustomerType = ECSVCustomerType::Investor;
	}
	else
	{
		CustomerType = ECSVCustomerType::Whale;
	}

	SetCustomerTypeDefaults();
	GenerateRandomPreferences();

	// Apply wealth multiplier from show tier
	Budget *= WealthMultiplier;

	UE_LOG(LogCardShowVendor, Verbose, TEXT("Customer initialized: Type %d, Budget $%.2f"),
		(int32)CustomerType, Budget);
}

void ACSVCustomer::SetCustomerTypeDefaults()
{
	switch (CustomerType)
	{
	case ECSVCustomerType::Casual:
		Budget = FMath::FRandRange(20.0f, 100.0f);
		Patience = FMath::FRandRange(30.0f, 60.0f);
		HaggleSkill = FMath::FRandRange(0.2f, 0.5f);
		KnowledgeLevel = FMath::FRandRange(0.2f, 0.5f);
		break;

	case ECSVCustomerType::Dedicated:
		Budget = FMath::FRandRange(100.0f, 500.0f);
		Patience = FMath::FRandRange(60.0f, 120.0f);
		HaggleSkill = FMath::FRandRange(0.4f, 0.7f);
		KnowledgeLevel = FMath::FRandRange(0.6f, 0.9f);
		break;

	case ECSVCustomerType::Investor:
		Budget = FMath::FRandRange(500.0f, 5000.0f);
		Patience = FMath::FRandRange(90.0f, 180.0f);
		HaggleSkill = FMath::FRandRange(0.7f, 0.95f);
		KnowledgeLevel = FMath::FRandRange(0.8f, 1.0f);
		break;

	case ECSVCustomerType::Flipper:
		Budget = FMath::FRandRange(200.0f, 1000.0f);
		Patience = FMath::FRandRange(20.0f, 40.0f);
		HaggleSkill = FMath::FRandRange(0.8f, 1.0f);
		KnowledgeLevel = FMath::FRandRange(0.7f, 0.95f);
		Preferences.bLookingForDeals = true;
		break;

	case ECSVCustomerType::Whale:
		Budget = FMath::FRandRange(2000.0f, 20000.0f);
		Patience = FMath::FRandRange(120.0f, 240.0f);
		HaggleSkill = FMath::FRandRange(0.3f, 0.6f); // Whales don't haggle much
		KnowledgeLevel = FMath::FRandRange(0.5f, 0.8f);
		Preferences.MinRarityInterest = 3; // Only interested in rare+
		break;

	case ECSVCustomerType::Newbie:
		Budget = FMath::FRandRange(10.0f, 50.0f);
		Patience = FMath::FRandRange(45.0f, 90.0f);
		HaggleSkill = FMath::FRandRange(0.0f, 0.3f);
		KnowledgeLevel = FMath::FRandRange(0.0f, 0.2f);
		break;
	}
}

void ACSVCustomer::GenerateRandomPreferences()
{
	// Random sport preferences
	TArray<FName> AllSports = { TEXT("Baseball"), TEXT("Basketball"), TEXT("Football"), TEXT("Pokemon"), TEXT("MagicTheGathering") };

	int32 NumPreferredSports = FMath::RandRange(1, 3);
	for (int32 i = 0; i < NumPreferredSports && AllSports.Num() > 0; ++i)
	{
		int32 Index = FMath::RandRange(0, AllSports.Num() - 1);
		Preferences.PreferredSports.Add(AllSports[Index]);
		AllSports.RemoveAt(Index);
	}

	// Era preference
	float EraRoll = FMath::FRand();
	if (EraRoll < 0.3f)
	{
		Preferences.bPrefersVintage = true;
	}
	else if (EraRoll > 0.7f)
	{
		Preferences.bPrefersModern = true;
	}

	// Deal seekers
	if (CustomerType == ECSVCustomerType::Flipper || FMath::FRand() < 0.2f)
	{
		Preferences.bLookingForDeals = true;
	}
}

void ACSVCustomer::SetTargetBooth(ACSVVendorBooth* Booth)
{
	TargetBooth = Booth;
	if (Booth)
	{
		CurrentState = ECSVCustomerState::ApproachingBooth;
	}
}

void ACSVCustomer::StartBrowsing()
{
	CurrentState = ECSVCustomerState::Browsing;
	BrowseTimer = 0.0f;
	PatienceTimer = Patience;
	CardsExamined = 0;
	InterestedCards.Empty();

	UE_LOG(LogCardShowVendor, Verbose, TEXT("Customer started browsing"));
}

void ACSVCustomer::StopBrowsing()
{
	if (CurrentState == ECSVCustomerState::Browsing)
	{
		CurrentState = ECSVCustomerState::Leaving;
	}
}

bool ACSVCustomer::IsInterestedInCard(UCSVCardInstance* Card) const
{
	if (!Card)
	{
		return false;
	}

	// Check rarity preference
	int32 CardRarity = Card->GetRarity();
	if (CardRarity < Preferences.MinRarityInterest || CardRarity > Preferences.MaxRarityInterest)
	{
		return false;
	}

	// Check sport preference
	FName CardSport = Card->GetSport();
	if (Preferences.PreferredSports.Num() > 0 && !Preferences.PreferredSports.Contains(CardSport))
	{
		// 30% chance to still be interested even if not preferred sport
		if (FMath::FRand() > 0.3f)
		{
			return false;
		}
	}

	// Check budget
	float CardValue = Card->GetMarketValue();
	if (CardValue > Budget * 1.5f) // Won't look at cards way over budget
	{
		return false;
	}

	// Random interest factor based on knowledge
	float InterestChance = 0.5f + (KnowledgeLevel * 0.3f);
	return FMath::FRand() < InterestChance;
}

float ACSVCustomer::CalculateWillingToPay(UCSVCardInstance* Card) const
{
	if (!Card)
	{
		return 0.0f;
	}

	float MarketValue = Card->GetMarketValue();
	float PerceivedValue = MarketValue;

	// Knowledge affects how accurately they perceive value
	float KnowledgeVariance = (1.0f - KnowledgeLevel) * 0.3f;
	float ValueModifier = FMath::FRandRange(1.0f - KnowledgeVariance, 1.0f + KnowledgeVariance);
	PerceivedValue *= ValueModifier;

	// Customer type modifiers
	switch (CustomerType)
	{
	case ECSVCustomerType::Casual:
		PerceivedValue *= 0.9f; // Slightly undervalues
		break;
	case ECSVCustomerType::Dedicated:
		// Pays fair price for cards they want
		break;
	case ECSVCustomerType::Investor:
		PerceivedValue *= 0.85f; // Looking for investment value
		break;
	case ECSVCustomerType::Flipper:
		PerceivedValue *= 0.7f; // Only buys if they can profit
		break;
	case ECSVCustomerType::Whale:
		PerceivedValue *= 1.2f; // Willing to pay premium
		break;
	case ECSVCustomerType::Newbie:
		PerceivedValue *= FMath::FRandRange(0.8f, 1.3f); // Very inconsistent
		break;
	}

	// Deal seekers expect discounts
	if (Preferences.bLookingForDeals)
	{
		PerceivedValue *= 0.8f;
	}

	// Cap at budget
	return FMath::Min(PerceivedValue, Budget);
}

bool ACSVCustomer::AttemptPurchase(UCSVCardInstance* Card, float AskingPrice)
{
	if (!Card || !HasBudgetFor(AskingPrice))
	{
		return false;
	}

	float WillingToPay = CalculateWillingToPay(Card);

	// Immediate purchase if price is good
	if (AskingPrice <= WillingToPay)
	{
		CompletePurchase(Card, AskingPrice);
		return true;
	}

	// Haggling
	float PriceGap = AskingPrice - WillingToPay;
	float GapPercent = PriceGap / AskingPrice;

	// If gap is too large, reject outright
	if (GapPercent > 0.4f)
	{
		OffersRejected++;
		return false;
	}

	// Attempt counter-offer based on haggle skill
	if (FMath::FRand() < HaggleSkill)
	{
		float CounterOffer = MakeCounterOffer(AskingPrice, WillingToPay);
		UE_LOG(LogCardShowVendor, Verbose, TEXT("Customer counter-offers $%.2f for $%.2f asking"),
			CounterOffer, AskingPrice);
		// Counter offer would be handled by UI/negotiation system
	}

	return false;
}

float ACSVCustomer::MakeCounterOffer(float AskingPrice, float PerceivedValue)
{
	// Start between perceived value and asking price
	float BaseOffer = FMath::Lerp(PerceivedValue, AskingPrice, 0.3f);

	// Haggle skill affects how aggressive the offer is
	float HaggleModifier = 1.0f - (HaggleSkill * 0.15f);
	float Offer = BaseOffer * HaggleModifier;

	// Never offer more than budget
	return FMath::Min(Offer, Budget);
}

void ACSVCustomer::CompletePurchase(UCSVCardInstance* Card, float FinalPrice)
{
	Budget -= FinalPrice;
	CurrentState = ECSVCustomerState::Purchasing;

	UE_LOG(LogCardShowVendor, Log, TEXT("Customer purchased card for $%.2f, remaining budget: $%.2f"),
		FinalPrice, Budget);

	// After purchase, decide whether to continue shopping
	if (Budget < 5.0f || FMath::FRand() < 0.3f)
	{
		CurrentState = ECSVCustomerState::Leaving;
	}
	else
	{
		CurrentState = ECSVCustomerState::Browsing;
	}
}

void ACSVCustomer::LeaveWithoutPurchase()
{
	CurrentState = ECSVCustomerState::Leaving;
	UE_LOG(LogCardShowVendor, Verbose, TEXT("Customer leaving without purchase"));
}

void ACSVCustomer::UpdateBehavior(float DeltaTime)
{
	switch (CurrentState)
	{
	case ECSVCustomerState::Wandering:
		// AI movement handled by behavior tree or simple wandering
		break;

	case ECSVCustomerState::ApproachingBooth:
		if (TargetBooth)
		{
			// Move towards booth - simplified, real impl would use AI navigation
			FVector Direction = TargetBooth->GetActorLocation() - GetActorLocation();
			if (Direction.Size() < 200.0f)
			{
				StartBrowsing();
			}
		}
		break;

	case ECSVCustomerState::Browsing:
		BrowseTimer += DeltaTime;
		PatienceTimer -= DeltaTime;

		if (PatienceTimer <= 0.0f)
		{
			LeaveWithoutPurchase();
		}
		break;

	case ECSVCustomerState::Negotiating:
		// Handled by negotiation system
		break;

	case ECSVCustomerState::Purchasing:
		// Brief pause during purchase animation
		break;

	case ECSVCustomerState::Leaving:
		// Move away from booth and despawn
		break;
	}
}
