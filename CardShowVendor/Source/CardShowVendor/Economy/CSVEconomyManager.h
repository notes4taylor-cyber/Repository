// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CSVEconomyManager.generated.h"

class UCSVCardData;
class UCSVCardInstance;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnMarketPriceChanged, FName, CardID, float, NewPrice);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnMarketEvent, const FString&, EventDescription);

UENUM(BlueprintType)
enum class ECSVMarketTrend : uint8
{
	Crashing		UMETA(DisplayName = "Market Crash"),
	Declining		UMETA(DisplayName = "Declining"),
	Stable			UMETA(DisplayName = "Stable"),
	Rising			UMETA(DisplayName = "Rising"),
	Booming			UMETA(DisplayName = "Market Boom")
};

USTRUCT(BlueprintType)
struct FCSVMarketModifier
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName ModifierName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText Description;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float PriceMultiplier = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float DemandMultiplier = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float DurationHours = 24.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<FName> AffectedSports;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<FName> AffectedPlayers;

	UPROPERTY()
	float RemainingDuration = 0.0f;
};

USTRUCT(BlueprintType)
struct FCSVPriceHistory
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly)
	TArray<float> PricePoints;

	UPROPERTY(BlueprintReadOnly)
	TArray<float> Timestamps;

	void AddDataPoint(float Price, float Time)
	{
		PricePoints.Add(Price);
		Timestamps.Add(Time);

		// Keep only last 100 data points
		if (PricePoints.Num() > 100)
		{
			PricePoints.RemoveAt(0);
			Timestamps.RemoveAt(0);
		}
	}

	float GetAveragePrice() const
	{
		if (PricePoints.Num() == 0) return 0.0f;
		float Sum = 0.0f;
		for (float Price : PricePoints) Sum += Price;
		return Sum / PricePoints.Num();
	}

	float GetPriceChange() const
	{
		if (PricePoints.Num() < 2) return 0.0f;
		return PricePoints.Last() - PricePoints[0];
	}
};

UCLASS(Blueprintable, BlueprintType)
class CARDSHOWVENDOR_API UCSVEconomyManager : public UObject
{
	GENERATED_BODY()

public:
	UCSVEconomyManager();

	// Initialization
	UFUNCTION(BlueprintCallable, Category = "Economy")
	void Initialize();

	UFUNCTION(BlueprintCallable, Category = "Economy")
	void TickEconomy(float DeltaTime);

	// Price calculations
	UFUNCTION(BlueprintCallable, Category = "Economy|Pricing")
	float GetCurrentMarketPrice(UCSVCardData* CardData) const;

	UFUNCTION(BlueprintCallable, Category = "Economy|Pricing")
	float GetCurrentMarketPrice_Instance(UCSVCardInstance* CardInstance) const;

	UFUNCTION(BlueprintCallable, Category = "Economy|Pricing")
	float CalculateSellPrice(UCSVCardInstance* CardInstance, float ConditionMultiplier = 1.0f) const;

	UFUNCTION(BlueprintCallable, Category = "Economy|Pricing")
	float CalculateBuyPrice(UCSVCardData* CardData) const;

	UFUNCTION(BlueprintPure, Category = "Economy|Pricing")
	float GetPriceModifierForSport(FName Sport) const;

	UFUNCTION(BlueprintPure, Category = "Economy|Pricing")
	float GetPriceModifierForPlayer(FName PlayerName) const;

	// Market trends
	UFUNCTION(BlueprintPure, Category = "Economy|Market")
	ECSVMarketTrend GetOverallMarketTrend() const { return OverallTrend; }

	UFUNCTION(BlueprintPure, Category = "Economy|Market")
	ECSVMarketTrend GetSportMarketTrend(FName Sport) const;

	UFUNCTION(BlueprintCallable, Category = "Economy|Market")
	void ApplyMarketModifier(const FCSVMarketModifier& Modifier);

	UFUNCTION(BlueprintCallable, Category = "Economy|Market")
	void TriggerMarketEvent();

	// Price history
	UFUNCTION(BlueprintPure, Category = "Economy|History")
	FCSVPriceHistory GetPriceHistory(FName CardID) const;

	UFUNCTION(BlueprintCallable, Category = "Economy|History")
	void RecordTransaction(FName CardID, float Price);

	// Delegates
	UPROPERTY(BlueprintAssignable, Category = "Economy|Events")
	FOnMarketPriceChanged OnMarketPriceChanged;

	UPROPERTY(BlueprintAssignable, Category = "Economy|Events")
	FOnMarketEvent OnMarketEvent;

protected:
	UPROPERTY()
	ECSVMarketTrend OverallTrend;

	UPROPERTY()
	TMap<FName, float> SportPriceModifiers;

	UPROPERTY()
	TMap<FName, float> PlayerPriceModifiers;

	UPROPERTY()
	TMap<FName, ECSVMarketTrend> SportTrends;

	UPROPERTY()
	TArray<FCSVMarketModifier> ActiveModifiers;

	UPROPERTY()
	TMap<FName, FCSVPriceHistory> PriceHistories;

	UPROPERTY()
	float TotalGameTime;

	UPROPERTY()
	float MarketUpdateTimer;

	UPROPERTY()
	float EventTimer;

	void UpdateMarketTrends();
	void ProcessActiveModifiers(float DeltaTime);
	void GenerateRandomEvent();
	float CalculateBaseModifier() const;
};
