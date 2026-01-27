// Copyright Card Show Vendor. All Rights Reserved.

#include "Economy/CSVProgressionManager.h"
#include "CardShowVendor.h"

UCSVProgressionManager::UCSVProgressionManager()
{
	CurrentLevel = 1;
	CurrentTier = 0;
	CurrentReputation = 0;
	ReputationToNextLevel = 100;
}

void UCSVProgressionManager::Initialize()
{
	InitializeAchievements();
	InitializeTierRequirements();

	ReputationToNextLevel = CalculateReputationForLevel(CurrentLevel + 1);

	UE_LOG(LogCardShowVendor, Log, TEXT("Progression Manager initialized - Level %d, Tier %d"),
		CurrentLevel, CurrentTier);
}

void UCSVProgressionManager::LoadProgression()
{
	// In a full implementation, this would load from save game
	UE_LOG(LogCardShowVendor, Log, TEXT("Loading progression data..."));
}

void UCSVProgressionManager::SaveProgression()
{
	// In a full implementation, this would save to save game
	UE_LOG(LogCardShowVendor, Log, TEXT("Saving progression data..."));
}

void UCSVProgressionManager::InitializeAchievements()
{
	Achievements.Empty();

	// Sales achievements
	FCSVAchievement FirstSale;
	FirstSale.AchievementID = TEXT("FIRST_SALE");
	FirstSale.AchievementName = FText::FromString(TEXT("First Sale"));
	FirstSale.Description = FText::FromString(TEXT("Sell your first card"));
	FirstSale.ReputationReward = 10;
	FirstSale.RequiredProgress = 1;
	Achievements.Add(FirstSale);

	FCSVAchievement HundredSales;
	HundredSales.AchievementID = TEXT("HUNDRED_SALES");
	HundredSales.AchievementName = FText::FromString(TEXT("Century Club"));
	HundredSales.Description = FText::FromString(TEXT("Sell 100 cards"));
	HundredSales.ReputationReward = 50;
	HundredSales.RequiredProgress = 100;
	Achievements.Add(HundredSales);

	FCSVAchievement ThousandSales;
	ThousandSales.AchievementID = TEXT("THOUSAND_SALES");
	ThousandSales.AchievementName = FText::FromString(TEXT("Sales Machine"));
	ThousandSales.Description = FText::FromString(TEXT("Sell 1000 cards"));
	ThousandSales.ReputationReward = 200;
	ThousandSales.MoneyReward = 500.0f;
	ThousandSales.RequiredProgress = 1000;
	Achievements.Add(ThousandSales);

	// Revenue achievements
	FCSVAchievement FirstHundred;
	FirstHundred.AchievementID = TEXT("FIRST_HUNDRED");
	FirstHundred.AchievementName = FText::FromString(TEXT("Breaking Even"));
	FirstHundred.Description = FText::FromString(TEXT("Earn $100 in total revenue"));
	FirstHundred.ReputationReward = 15;
	FirstHundred.RequiredProgress = 100;
	Achievements.Add(FirstHundred);

	FCSVAchievement FirstThousand;
	FirstThousand.AchievementID = TEXT("FIRST_THOUSAND");
	FirstThousand.AchievementName = FText::FromString(TEXT("In the Money"));
	FirstThousand.Description = FText::FromString(TEXT("Earn $1,000 in total revenue"));
	FirstThousand.ReputationReward = 50;
	FirstThousand.RequiredProgress = 1000;
	Achievements.Add(FirstThousand);

	FCSVAchievement TenThousand;
	TenThousand.AchievementID = TEXT("TEN_THOUSAND");
	TenThousand.AchievementName = FText::FromString(TEXT("Serious Dealer"));
	TenThousand.Description = FText::FromString(TEXT("Earn $10,000 in total revenue"));
	TenThousand.ReputationReward = 150;
	TenThousand.MoneyReward = 250.0f;
	TenThousand.RequiredProgress = 10000;
	Achievements.Add(TenThousand);

	FCSVAchievement HundredThousand;
	HundredThousand.AchievementID = TEXT("HUNDRED_THOUSAND");
	HundredThousand.AchievementName = FText::FromString(TEXT("Card Mogul"));
	HundredThousand.Description = FText::FromString(TEXT("Earn $100,000 in total revenue"));
	HundredThousand.ReputationReward = 500;
	HundredThousand.MoneyReward = 2500.0f;
	HundredThousand.RequiredProgress = 100000;
	Achievements.Add(HundredThousand);

	// Big sale achievements
	FCSVAchievement BigSale;
	BigSale.AchievementID = TEXT("BIG_SALE");
	BigSale.AchievementName = FText::FromString(TEXT("Big Ticket"));
	BigSale.Description = FText::FromString(TEXT("Make a single sale of $100 or more"));
	BigSale.ReputationReward = 25;
	BigSale.RequiredProgress = 100;
	Achievements.Add(BigSale);

	FCSVAchievement WhaleSale;
	WhaleSale.AchievementID = TEXT("WHALE_SALE");
	WhaleSale.AchievementName = FText::FromString(TEXT("Whale Watcher"));
	WhaleSale.Description = FText::FromString(TEXT("Make a single sale of $1,000 or more"));
	WhaleSale.ReputationReward = 100;
	WhaleSale.RequiredProgress = 1000;
	Achievements.Add(WhaleSale);

	// Show achievements
	FCSVAchievement FirstShow;
	FirstShow.AchievementID = TEXT("FIRST_SHOW");
	FirstShow.AchievementName = FText::FromString(TEXT("Show Time"));
	FirstShow.Description = FText::FromString(TEXT("Attend your first card show"));
	FirstShow.ReputationReward = 10;
	FirstShow.RequiredProgress = 1;
	Achievements.Add(FirstShow);

	FCSVAchievement ShowVeteran;
	ShowVeteran.AchievementID = TEXT("SHOW_VETERAN");
	ShowVeteran.AchievementName = FText::FromString(TEXT("Show Veteran"));
	ShowVeteran.Description = FText::FromString(TEXT("Attend 25 card shows"));
	ShowVeteran.ReputationReward = 75;
	ShowVeteran.RequiredProgress = 25;
	Achievements.Add(ShowVeteran);

	// Rare card achievements
	FCSVAchievement FirstRare;
	FirstRare.AchievementID = TEXT("FIRST_RARE");
	FirstRare.AchievementName = FText::FromString(TEXT("Rare Find"));
	FirstRare.Description = FText::FromString(TEXT("Find your first rare card"));
	FirstRare.ReputationReward = 15;
	FirstRare.RequiredProgress = 1;
	Achievements.Add(FirstRare);

	FCSVAchievement FirstLegendary;
	FirstLegendary.AchievementID = TEXT("FIRST_LEGENDARY");
	FirstLegendary.AchievementName = FText::FromString(TEXT("Legendary Pull"));
	FirstLegendary.Description = FText::FromString(TEXT("Find your first legendary card"));
	FirstLegendary.ReputationReward = 50;
	FirstLegendary.RequiredProgress = 1;
	Achievements.Add(FirstLegendary);

	// Pack opening achievements
	FCSVAchievement PackRat;
	PackRat.AchievementID = TEXT("PACK_RAT");
	PackRat.AchievementName = FText::FromString(TEXT("Pack Rat"));
	PackRat.Description = FText::FromString(TEXT("Open 100 packs"));
	PackRat.ReputationReward = 40;
	PackRat.RequiredProgress = 100;
	Achievements.Add(PackRat);

	UE_LOG(LogCardShowVendor, Log, TEXT("Initialized %d achievements"), Achievements.Num());
}

void UCSVProgressionManager::InitializeTierRequirements()
{
	TierRequirements.Empty();

	// Tier 0: Beginner
	FCSVTierRequirements Tier0;
	Tier0.RequiredReputation = 0;
	Tier0.RequiredShowsAttended = 0;
	Tier0.RequiredTotalRevenue = 0.0f;
	Tier0.TierName = FText::FromString(TEXT("Beginner Vendor"));
	Tier0.TierDescription = FText::FromString(TEXT("Just starting out in the card business"));
	TierRequirements.Add(Tier0);

	// Tier 1: Amateur
	FCSVTierRequirements Tier1;
	Tier1.RequiredReputation = 100;
	Tier1.RequiredShowsAttended = 3;
	Tier1.RequiredTotalRevenue = 500.0f;
	Tier1.TierName = FText::FromString(TEXT("Amateur Vendor"));
	Tier1.TierDescription = FText::FromString(TEXT("Getting the hang of selling cards"));
	TierRequirements.Add(Tier1);

	// Tier 2: Established
	FCSVTierRequirements Tier2;
	Tier2.RequiredReputation = 500;
	Tier2.RequiredShowsAttended = 10;
	Tier2.RequiredTotalRevenue = 2500.0f;
	Tier2.TierName = FText::FromString(TEXT("Established Vendor"));
	Tier2.TierDescription = FText::FromString(TEXT("A recognized face at local shows"));
	TierRequirements.Add(Tier2);

	// Tier 3: Professional
	FCSVTierRequirements Tier3;
	Tier3.RequiredReputation = 1500;
	Tier3.RequiredShowsAttended = 25;
	Tier3.RequiredTotalRevenue = 10000.0f;
	Tier3.TierName = FText::FromString(TEXT("Professional Vendor"));
	Tier3.TierDescription = FText::FromString(TEXT("Making a living in the card business"));
	TierRequirements.Add(Tier3);

	// Tier 4: Expert
	FCSVTierRequirements Tier4;
	Tier4.RequiredReputation = 5000;
	Tier4.RequiredShowsAttended = 50;
	Tier4.RequiredTotalRevenue = 50000.0f;
	Tier4.TierName = FText::FromString(TEXT("Expert Vendor"));
	Tier4.TierDescription = FText::FromString(TEXT("One of the top vendors in the region"));
	TierRequirements.Add(Tier4);

	// Tier 5: Elite
	FCSVTierRequirements Tier5;
	Tier5.RequiredReputation = 15000;
	Tier5.RequiredShowsAttended = 100;
	Tier5.RequiredTotalRevenue = 250000.0f;
	Tier5.TierName = FText::FromString(TEXT("Elite Vendor"));
	Tier5.TierDescription = FText::FromString(TEXT("A legendary name in the card collecting world"));
	TierRequirements.Add(Tier5);

	UE_LOG(LogCardShowVendor, Log, TEXT("Initialized %d tier requirements"), TierRequirements.Num());
}

void UCSVProgressionManager::AddReputation(int32 Amount)
{
	int32 OldReputation = CurrentReputation;
	CurrentReputation += Amount;
	CurrentReputation = FMath::Max(0, CurrentReputation);

	OnReputationChanged.Broadcast(CurrentReputation, Amount);

	CheckLevelUp();
	CheckTierUp();

	UE_LOG(LogCardShowVendor, Verbose, TEXT("Reputation changed: %d -> %d (%+d)"),
		OldReputation, CurrentReputation, Amount);
}

bool UCSVProgressionManager::CanAccessTier(int32 Tier) const
{
	if (Tier < 0 || Tier >= TierRequirements.Num())
	{
		return false;
	}

	const FCSVTierRequirements& Reqs = TierRequirements[Tier];

	return CurrentReputation >= Reqs.RequiredReputation &&
		   Stats.ShowsAttended >= Reqs.RequiredShowsAttended &&
		   Stats.TotalRevenue >= Reqs.RequiredTotalRevenue;
}

float UCSVProgressionManager::GetLevelProgress() const
{
	int32 CurrentLevelRep = CalculateReputationForLevel(CurrentLevel);
	int32 NextLevelRep = CalculateReputationForLevel(CurrentLevel + 1);

	float Progress = (float)(CurrentReputation - CurrentLevelRep) / (NextLevelRep - CurrentLevelRep);
	return FMath::Clamp(Progress, 0.0f, 1.0f);
}

void UCSVProgressionManager::RecordSale(float Amount, int32 CardRarity)
{
	Stats.TotalCardsSold++;
	Stats.TotalRevenue += Amount;

	if (Amount > Stats.HighestSingleSale)
	{
		Stats.HighestSingleSale = Amount;
	}

	// Update achievement progress
	for (FCSVAchievement& Achievement : Achievements)
	{
		if (!Achievement.bUnlocked)
		{
			if (Achievement.AchievementID == TEXT("FIRST_SALE") ||
				Achievement.AchievementID == TEXT("HUNDRED_SALES") ||
				Achievement.AchievementID == TEXT("THOUSAND_SALES"))
			{
				Achievement.Progress = Stats.TotalCardsSold;
			}
			else if (Achievement.AchievementID == TEXT("FIRST_HUNDRED") ||
					 Achievement.AchievementID == TEXT("FIRST_THOUSAND") ||
					 Achievement.AchievementID == TEXT("TEN_THOUSAND") ||
					 Achievement.AchievementID == TEXT("HUNDRED_THOUSAND"))
			{
				Achievement.Progress = Stats.TotalRevenue;
			}
			else if (Achievement.AchievementID == TEXT("BIG_SALE") ||
					 Achievement.AchievementID == TEXT("WHALE_SALE"))
			{
				Achievement.Progress = FMath::Max(Achievement.Progress, Amount);
			}
		}
	}

	CheckAchievements();
}

void UCSVProgressionManager::RecordPurchase(float Amount)
{
	Stats.TotalCardsBought++;
	Stats.TotalSpent += Amount;
}

void UCSVProgressionManager::RecordShowAttended()
{
	Stats.ShowsAttended++;

	// Update achievement progress
	for (FCSVAchievement& Achievement : Achievements)
	{
		if (!Achievement.bUnlocked)
		{
			if (Achievement.AchievementID == TEXT("FIRST_SHOW") ||
				Achievement.AchievementID == TEXT("SHOW_VETERAN"))
			{
				Achievement.Progress = Stats.ShowsAttended;
			}
		}
	}

	CheckAchievements();
	CheckTierUp();
}

void UCSVProgressionManager::RecordCustomerServed()
{
	Stats.CustomersServed++;
}

void UCSVProgressionManager::RecordPackOpened(int32 RaresFound, int32 LegendariesFound)
{
	Stats.PacksOpened++;
	Stats.RareCardsFound += RaresFound;
	Stats.LegendaryCardsFound += LegendariesFound;

	// Update achievement progress
	for (FCSVAchievement& Achievement : Achievements)
	{
		if (!Achievement.bUnlocked)
		{
			if (Achievement.AchievementID == TEXT("FIRST_RARE"))
			{
				Achievement.Progress = Stats.RareCardsFound;
			}
			else if (Achievement.AchievementID == TEXT("FIRST_LEGENDARY"))
			{
				Achievement.Progress = Stats.LegendaryCardsFound;
			}
			else if (Achievement.AchievementID == TEXT("PACK_RAT"))
			{
				Achievement.Progress = Stats.PacksOpened;
			}
		}
	}

	CheckAchievements();
}

void UCSVProgressionManager::UpdatePlayTime(float DeltaHours)
{
	Stats.PlayTimeHours += DeltaHours;
}

void UCSVProgressionManager::CheckAchievements()
{
	for (FCSVAchievement& Achievement : Achievements)
	{
		if (!Achievement.bUnlocked && Achievement.Progress >= Achievement.RequiredProgress)
		{
			UnlockAchievement(Achievement.AchievementID);
		}
	}
}

void UCSVProgressionManager::UnlockAchievement(FName AchievementID)
{
	for (FCSVAchievement& Achievement : Achievements)
	{
		if (Achievement.AchievementID == AchievementID && !Achievement.bUnlocked)
		{
			Achievement.bUnlocked = true;

			// Grant rewards
			if (Achievement.ReputationReward > 0)
			{
				AddReputation(Achievement.ReputationReward);
			}

			OnAchievementUnlocked.Broadcast(AchievementID);

			UE_LOG(LogCardShowVendor, Log, TEXT("Achievement unlocked: %s"),
				*Achievement.AchievementName.ToString());
			break;
		}
	}
}

bool UCSVProgressionManager::IsAchievementUnlocked(FName AchievementID) const
{
	for (const FCSVAchievement& Achievement : Achievements)
	{
		if (Achievement.AchievementID == AchievementID)
		{
			return Achievement.bUnlocked;
		}
	}
	return false;
}

TArray<FCSVAchievement> UCSVProgressionManager::GetUnlockedAchievements() const
{
	TArray<FCSVAchievement> UnlockedList;
	for (const FCSVAchievement& Achievement : Achievements)
	{
		if (Achievement.bUnlocked)
		{
			UnlockedList.Add(Achievement);
		}
	}
	return UnlockedList;
}

void UCSVProgressionManager::UnlockFeature(FName FeatureID)
{
	if (!UnlockedFeatures.Contains(FeatureID))
	{
		UnlockedFeatures.Add(FeatureID);
		UE_LOG(LogCardShowVendor, Log, TEXT("Feature unlocked: %s"), *FeatureID.ToString());
	}
}

bool UCSVProgressionManager::IsFeatureUnlocked(FName FeatureID) const
{
	return UnlockedFeatures.Contains(FeatureID);
}

void UCSVProgressionManager::CheckLevelUp()
{
	int32 OldLevel = CurrentLevel;

	while (CurrentReputation >= CalculateReputationForLevel(CurrentLevel + 1))
	{
		CurrentLevel++;
	}

	ReputationToNextLevel = CalculateReputationForLevel(CurrentLevel + 1);

	if (CurrentLevel > OldLevel)
	{
		OnLevelUp.Broadcast(CurrentLevel, CurrentTier);
		UE_LOG(LogCardShowVendor, Log, TEXT("Level up! Now level %d"), CurrentLevel);
	}
}

void UCSVProgressionManager::CheckTierUp()
{
	int32 OldTier = CurrentTier;

	for (int32 i = TierRequirements.Num() - 1; i > CurrentTier; --i)
	{
		if (CanAccessTier(i))
		{
			CurrentTier = i;
			break;
		}
	}

	if (CurrentTier > OldTier)
	{
		OnLevelUp.Broadcast(CurrentLevel, CurrentTier);
		OnMilestoneReached.Broadcast(*FString::Printf(TEXT("TIER_%d"), CurrentTier));
		UE_LOG(LogCardShowVendor, Log, TEXT("Tier up! Now tier %d"), CurrentTier);
	}
}

int32 UCSVProgressionManager::CalculateReputationForLevel(int32 Level) const
{
	// Exponential growth formula
	// Level 1: 0, Level 2: 100, Level 3: 225, etc.
	if (Level <= 1) return 0;
	return FMath::FloorToInt(100.0f * FMath::Pow(1.5f, Level - 2));
}
