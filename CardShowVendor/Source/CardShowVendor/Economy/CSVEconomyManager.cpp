// Copyright Card Show Vendor. All Rights Reserved.

#include "Economy/CSVEconomyManager.h"
#include "Cards/CSVCardData.h"
#include "Cards/CSVCardInstance.h"
#include "CardShowVendor.h"

UCSVEconomyManager::UCSVEconomyManager()
{
	OverallTrend = ECSVMarketTrend::Stable;
	TotalGameTime = 0.0f;
	MarketUpdateTimer = 0.0f;
	EventTimer = 0.0f;
}

void UCSVEconomyManager::Initialize()
{
	// Initialize sport price modifiers
	SportPriceModifiers.Add(TEXT("Baseball"), 1.0f);
	SportPriceModifiers.Add(TEXT("Basketball"), 1.1f);
	SportPriceModifiers.Add(TEXT("Football"), 1.05f);
	SportPriceModifiers.Add(TEXT("Pokemon"), 1.15f);
	SportPriceModifiers.Add(TEXT("MagicTheGathering"), 0.95f);

	// Initialize sport trends
	SportTrends.Add(TEXT("Baseball"), ECSVMarketTrend::Stable);
	SportTrends.Add(TEXT("Basketball"), ECSVMarketTrend::Rising);
	SportTrends.Add(TEXT("Football"), ECSVMarketTrend::Stable);
	SportTrends.Add(TEXT("Pokemon"), ECSVMarketTrend::Booming);
	SportTrends.Add(TEXT("MagicTheGathering"), ECSVMarketTrend::Declining);

	// Some initial player modifiers for popular players
	PlayerPriceModifiers.Add(TEXT("Michael Jordan"), 1.5f);
	PlayerPriceModifiers.Add(TEXT("LeBron James"), 1.3f);
	PlayerPriceModifiers.Add(TEXT("Shohei Ohtani"), 1.4f);
	PlayerPriceModifiers.Add(TEXT("Charizard"), 1.6f);

	UE_LOG(LogCardShowVendor, Log, TEXT("Economy Manager initialized"));
}

void UCSVEconomyManager::TickEconomy(float DeltaTime)
{
	TotalGameTime += DeltaTime;
	MarketUpdateTimer += DeltaTime;
	EventTimer += DeltaTime;

	// Update market trends periodically (every game-hour)
	if (MarketUpdateTimer >= 60.0f) // 60 seconds = 1 game hour
	{
		MarketUpdateTimer = 0.0f;
		UpdateMarketTrends();
	}

	// Random market events
	if (EventTimer >= 300.0f) // Every 5 minutes, chance for event
	{
		EventTimer = 0.0f;
		if (FMath::FRand() < 0.3f) // 30% chance
		{
			GenerateRandomEvent();
		}
	}

	// Process active modifiers
	ProcessActiveModifiers(DeltaTime);
}

float UCSVEconomyManager::GetCurrentMarketPrice(UCSVCardData* CardData) const
{
	if (!CardData)
	{
		return 0.0f;
	}

	float BasePrice = CardData->BaseValue;

	// Apply sport modifier
	FName SportName = StaticEnum<ECSVCardSport>()->GetNameByValue((int64)CardData->Sport);
	float SportMod = GetPriceModifierForSport(SportName);

	// Apply player modifier if exists
	float PlayerMod = GetPriceModifierForPlayer(FName(*CardData->PlayerName.ToString()));

	// Apply market trend modifier
	float TrendMod = CalculateBaseModifier();

	// Apply active modifier effects
	float ActiveMod = 1.0f;
	for (const FCSVMarketModifier& Modifier : ActiveModifiers)
	{
		if (Modifier.AffectedSports.Num() == 0 || Modifier.AffectedSports.Contains(SportName))
		{
			ActiveMod *= Modifier.PriceMultiplier;
		}
	}

	float FinalPrice = BasePrice * SportMod * PlayerMod * TrendMod * ActiveMod;

	// Add some natural variance (±5%)
	float Variance = FMath::FRandRange(0.95f, 1.05f);
	FinalPrice *= Variance;

	return FMath::Max(0.01f, FinalPrice);
}

float UCSVEconomyManager::GetCurrentMarketPrice_Instance(UCSVCardInstance* CardInstance) const
{
	if (!CardInstance)
	{
		return 0.0f;
	}

	float BaseMarketPrice = CardInstance->GetMarketValue();

	// Apply condition multiplier
	float ConditionMod = CardInstance->GetConditionMultiplier();

	// Apply grading premium if graded
	float GradeMod = 1.0f;
	if (CardInstance->IsGraded())
	{
		GradeMod = CardInstance->GetGradeMultiplier();
	}

	// Apply serial number premium for numbered cards
	float SerialMod = 1.0f;
	if (CardInstance->HasSerialNumber())
	{
		int32 Serial = CardInstance->GetSerialNumber();
		int32 TotalPrint = CardInstance->GetTotalPrintRun();
		if (TotalPrint > 0)
		{
			// Lower serial numbers are more valuable
			float SerialRatio = (float)Serial / TotalPrint;
			if (SerialRatio <= 0.01f) // First 1%
			{
				SerialMod = 2.0f;
			}
			else if (SerialRatio <= 0.1f) // First 10%
			{
				SerialMod = 1.5f;
			}
			else
			{
				SerialMod = 1.0f + (1.0f - SerialRatio) * 0.2f;
			}
		}
	}

	return BaseMarketPrice * ConditionMod * GradeMod * SerialMod;
}

float UCSVEconomyManager::CalculateSellPrice(UCSVCardInstance* CardInstance, float ConditionMultiplier) const
{
	float MarketPrice = GetCurrentMarketPrice_Instance(CardInstance);

	// Vendors typically pay 60-80% of market value
	float BuyRate = FMath::FRandRange(0.6f, 0.8f);

	return MarketPrice * BuyRate * ConditionMultiplier;
}

float UCSVEconomyManager::CalculateBuyPrice(UCSVCardData* CardData) const
{
	float MarketPrice = GetCurrentMarketPrice(CardData);

	// Buying from vendors typically costs 100-120% of market value
	float SellRate = FMath::FRandRange(1.0f, 1.2f);

	return MarketPrice * SellRate;
}

float UCSVEconomyManager::GetPriceModifierForSport(FName Sport) const
{
	if (SportPriceModifiers.Contains(Sport))
	{
		return SportPriceModifiers[Sport];
	}
	return 1.0f;
}

float UCSVEconomyManager::GetPriceModifierForPlayer(FName PlayerName) const
{
	if (PlayerPriceModifiers.Contains(PlayerName))
	{
		return PlayerPriceModifiers[PlayerName];
	}
	return 1.0f;
}

ECSVMarketTrend UCSVEconomyManager::GetSportMarketTrend(FName Sport) const
{
	if (SportTrends.Contains(Sport))
	{
		return SportTrends[Sport];
	}
	return ECSVMarketTrend::Stable;
}

void UCSVEconomyManager::ApplyMarketModifier(const FCSVMarketModifier& Modifier)
{
	FCSVMarketModifier NewModifier = Modifier;
	NewModifier.RemainingDuration = Modifier.DurationHours * 60.0f; // Convert to seconds
	ActiveModifiers.Add(NewModifier);

	OnMarketEvent.Broadcast(Modifier.Description.ToString());

	UE_LOG(LogCardShowVendor, Log, TEXT("Market modifier applied: %s (%.1fx price for %.1f hours)"),
		*Modifier.ModifierName.ToString(), Modifier.PriceMultiplier, Modifier.DurationHours);
}

void UCSVEconomyManager::TriggerMarketEvent()
{
	GenerateRandomEvent();
}

FCSVPriceHistory UCSVEconomyManager::GetPriceHistory(FName CardID) const
{
	if (PriceHistories.Contains(CardID))
	{
		return PriceHistories[CardID];
	}
	return FCSVPriceHistory();
}

void UCSVEconomyManager::RecordTransaction(FName CardID, float Price)
{
	if (!PriceHistories.Contains(CardID))
	{
		PriceHistories.Add(CardID, FCSVPriceHistory());
	}
	PriceHistories[CardID].AddDataPoint(Price, TotalGameTime);
}

void UCSVEconomyManager::UpdateMarketTrends()
{
	// Overall trend shifts slowly
	float TrendShift = FMath::FRandRange(-0.1f, 0.1f);
	int32 CurrentTrend = (int32)OverallTrend;
	CurrentTrend = FMath::Clamp(CurrentTrend + FMath::RoundToInt(TrendShift * 5), 0, 4);
	OverallTrend = (ECSVMarketTrend)CurrentTrend;

	// Update sport-specific trends
	for (auto& Pair : SportTrends)
	{
		float SportShift = FMath::FRandRange(-0.15f, 0.15f);
		int32 SportTrend = (int32)Pair.Value;
		SportTrend = FMath::Clamp(SportTrend + FMath::RoundToInt(SportShift * 5), 0, 4);
		Pair.Value = (ECSVMarketTrend)SportTrend;
	}

	// Update price modifiers based on trends
	for (auto& Pair : SportPriceModifiers)
	{
		ECSVMarketTrend Trend = GetSportMarketTrend(Pair.Key);
		switch (Trend)
		{
		case ECSVMarketTrend::Crashing:
			Pair.Value *= 0.95f;
			break;
		case ECSVMarketTrend::Declining:
			Pair.Value *= 0.98f;
			break;
		case ECSVMarketTrend::Stable:
			// Small random walk
			Pair.Value *= FMath::FRandRange(0.99f, 1.01f);
			break;
		case ECSVMarketTrend::Rising:
			Pair.Value *= 1.02f;
			break;
		case ECSVMarketTrend::Booming:
			Pair.Value *= 1.05f;
			break;
		}
		// Keep modifiers in reasonable range
		Pair.Value = FMath::Clamp(Pair.Value, 0.5f, 2.0f);
	}
}

void UCSVEconomyManager::ProcessActiveModifiers(float DeltaTime)
{
	for (int32 i = ActiveModifiers.Num() - 1; i >= 0; --i)
	{
		ActiveModifiers[i].RemainingDuration -= DeltaTime;
		if (ActiveModifiers[i].RemainingDuration <= 0.0f)
		{
			UE_LOG(LogCardShowVendor, Log, TEXT("Market modifier expired: %s"),
				*ActiveModifiers[i].ModifierName.ToString());
			ActiveModifiers.RemoveAt(i);
		}
	}
}

void UCSVEconomyManager::GenerateRandomEvent()
{
	TArray<FCSVMarketModifier> PossibleEvents;

	// Positive events
	FCSVMarketModifier RookieBoom;
	RookieBoom.ModifierName = TEXT("RookieBoom");
	RookieBoom.Description = FText::FromString(TEXT("Rookie card market is booming! Prices up 20%"));
	RookieBoom.PriceMultiplier = 1.2f;
	RookieBoom.DurationHours = 2.0f;
	PossibleEvents.Add(RookieBoom);

	FCSVMarketModifier VintageSurge;
	VintageSurge.ModifierName = TEXT("VintageSurge");
	VintageSurge.Description = FText::FromString(TEXT("Collectors rushing for vintage! Pre-1980 cards +30%"));
	VintageSurge.PriceMultiplier = 1.3f;
	VintageSurge.DurationHours = 1.5f;
	PossibleEvents.Add(VintageSurge);

	FCSVMarketModifier PokemonHype;
	PokemonHype.ModifierName = TEXT("PokemonHype");
	PokemonHype.Description = FText::FromString(TEXT("New Pokemon set announcement! Pokemon cards +25%"));
	PokemonHype.PriceMultiplier = 1.25f;
	PokemonHype.DurationHours = 3.0f;
	PokemonHype.AffectedSports.Add(TEXT("Pokemon"));
	PossibleEvents.Add(PokemonHype);

	// Negative events
	FCSVMarketModifier MarketCorrection;
	MarketCorrection.ModifierName = TEXT("MarketCorrection");
	MarketCorrection.Description = FText::FromString(TEXT("Market correction in progress. All prices -15%"));
	MarketCorrection.PriceMultiplier = 0.85f;
	MarketCorrection.DurationHours = 2.0f;
	PossibleEvents.Add(MarketCorrection);

	FCSVMarketModifier GradingBacklog;
	GradingBacklog.ModifierName = TEXT("GradingBacklog");
	GradingBacklog.Description = FText::FromString(TEXT("Grading backlog announced. Raw card demand +10%"));
	GradingBacklog.PriceMultiplier = 1.1f;
	GradingBacklog.DemandMultiplier = 1.15f;
	GradingBacklog.DurationHours = 4.0f;
	PossibleEvents.Add(GradingBacklog);

	// Player-specific events
	FCSVMarketModifier HallOfFame;
	HallOfFame.ModifierName = TEXT("HallOfFame");
	HallOfFame.Description = FText::FromString(TEXT("Hall of Fame announcement! Featured player cards +40%"));
	HallOfFame.PriceMultiplier = 1.4f;
	HallOfFame.DurationHours = 2.0f;
	PossibleEvents.Add(HallOfFame);

	// Select and apply random event
	if (PossibleEvents.Num() > 0)
	{
		int32 EventIndex = FMath::RandRange(0, PossibleEvents.Num() - 1);
		ApplyMarketModifier(PossibleEvents[EventIndex]);
	}
}

float UCSVEconomyManager::CalculateBaseModifier() const
{
	switch (OverallTrend)
	{
	case ECSVMarketTrend::Crashing:
		return 0.7f;
	case ECSVMarketTrend::Declining:
		return 0.85f;
	case ECSVMarketTrend::Stable:
		return 1.0f;
	case ECSVMarketTrend::Rising:
		return 1.15f;
	case ECSVMarketTrend::Booming:
		return 1.3f;
	default:
		return 1.0f;
	}
}
