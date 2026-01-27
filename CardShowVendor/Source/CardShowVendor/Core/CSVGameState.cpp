// Copyright Card Show Vendor. All Rights Reserved.

#include "Core/CSVGameState.h"
#include "Shows/CSVCardShow.h"
#include "CardShowVendor.h"

ACSVGameState::ACSVGameState()
{
	Reputation = 0;
	CurrentDay = 1;
	TotalShowsAttended = 0;
	TotalCardsSold = 0;
	TotalCardsGraded = 0;
	TotalRevenue = 0.0f;
	CustomersServed = 0;
	RareCardsPulled = 0;

	InitializeDefaults();
}

void ACSVGameState::BeginPlay()
{
	Super::BeginPlay();
}

void ACSVGameState::InitializeDefaults()
{
	// Default tier thresholds
	TierReputationThresholds.Empty();
	TierReputationThresholds.Add(0);     // Tier 0: Rookie
	TierReputationThresholds.Add(100);   // Tier 1: Amateur
	TierReputationThresholds.Add(250);   // Tier 2: Established
	TierReputationThresholds.Add(500);   // Tier 3: Professional
	TierReputationThresholds.Add(750);   // Tier 4: Expert
	TierReputationThresholds.Add(900);   // Tier 5: Legend

	// Rank names
	VendorRankNames.Empty();
	VendorRankNames.Add(TEXT("Rookie Vendor"));
	VendorRankNames.Add(TEXT("Amateur Dealer"));
	VendorRankNames.Add(TEXT("Established Seller"));
	VendorRankNames.Add(TEXT("Professional Trader"));
	VendorRankNames.Add(TEXT("Expert Collector"));
	VendorRankNames.Add(TEXT("Legendary Vendor"));
}

void ACSVGameState::AddReputation(int32 Amount)
{
	int32 OldReputation = Reputation;
	Reputation = FMath::Clamp(Reputation + Amount, 0, MaxReputation);

	if (Reputation != OldReputation)
	{
		OnReputationChanged.Broadcast(Reputation);

		// Check for tier up
		int32 OldTier = 0;
		int32 NewTier = GetVendorTier();
		for (int32 i = TierReputationThresholds.Num() - 1; i >= 0; --i)
		{
			if (OldReputation >= TierReputationThresholds[i])
			{
				OldTier = i;
				break;
			}
		}

		if (NewTier > OldTier)
		{
			UE_LOG(LogCardShowVendor, Log, TEXT("Vendor ranked up to: %s"), *GetVendorRankName());
		}
	}
}

int32 ACSVGameState::GetVendorTier() const
{
	for (int32 i = TierReputationThresholds.Num() - 1; i >= 0; --i)
	{
		if (Reputation >= TierReputationThresholds[i])
		{
			return i;
		}
	}
	return 0;
}

FString ACSVGameState::GetVendorRankName() const
{
	int32 Tier = GetVendorTier();
	if (VendorRankNames.IsValidIndex(Tier))
	{
		return VendorRankNames[Tier];
	}
	return TEXT("Unknown");
}

void ACSVGameState::AdvanceDay()
{
	CurrentDay++;
	OnDayChanged.Broadcast(CurrentDay);
	UE_LOG(LogCardShowVendor, Log, TEXT("Advanced to Day %d"), CurrentDay);
}

void ACSVGameState::OnShowCompleted(ACSVCardShow* CompletedShow)
{
	if (!CompletedShow)
	{
		return;
	}

	TotalShowsAttended++;

	// Get stats from the show
	TotalCardsSold += CompletedShow->GetCardsSoldThisShow();
	TotalRevenue += CompletedShow->GetRevenueThisShow();
	CustomersServed += CompletedShow->GetCustomersServedThisShow();

	// Calculate reputation gain based on performance
	int32 RepGain = CompletedShow->CalculateReputationGain();
	AddReputation(RepGain);

	OnShowCompletedDelegate.Broadcast();

	UE_LOG(LogCardShowVendor, Log, TEXT("Show completed - Cards Sold: %d, Revenue: $%.2f, Rep Gained: %d"),
		CompletedShow->GetCardsSoldThisShow(), CompletedShow->GetRevenueThisShow(), RepGain);
}
