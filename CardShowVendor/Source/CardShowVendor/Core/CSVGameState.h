// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameStateBase.h"
#include "CSVGameState.generated.h"

class ACSVCardShow;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnReputationChanged, int32, NewReputation);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDayChanged, int32, NewDay);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnShowCompleted);

/**
 * Game State for Card Show Vendor
 * Tracks overall game progression, reputation, and statistics
 */
UCLASS()
class CARDSHOWVENDOR_API ACSVGameState : public AGameStateBase
{
	GENERATED_BODY()

public:
	ACSVGameState();

	virtual void BeginPlay() override;

	// Reputation system
	UPROPERTY(BlueprintReadOnly, Category = "Reputation")
	int32 Reputation;

	UPROPERTY(EditDefaultsOnly, Category = "Reputation")
	int32 MaxReputation = 1000;

	UFUNCTION(BlueprintCallable, Category = "Reputation")
	void AddReputation(int32 Amount);

	UFUNCTION(BlueprintPure, Category = "Reputation")
	int32 GetVendorTier() const;

	UFUNCTION(BlueprintPure, Category = "Reputation")
	FString GetVendorRankName() const;

	// Day/Calendar system
	UPROPERTY(BlueprintReadOnly, Category = "Calendar")
	int32 CurrentDay;

	UPROPERTY(BlueprintReadOnly, Category = "Calendar")
	int32 TotalShowsAttended;

	UFUNCTION(BlueprintCallable, Category = "Calendar")
	void AdvanceDay();

	// Statistics
	UPROPERTY(BlueprintReadOnly, Category = "Statistics")
	int32 TotalCardsSold;

	UPROPERTY(BlueprintReadOnly, Category = "Statistics")
	int32 TotalCardsGraded;

	UPROPERTY(BlueprintReadOnly, Category = "Statistics")
	float TotalRevenue;

	UPROPERTY(BlueprintReadOnly, Category = "Statistics")
	int32 CustomersServed;

	UPROPERTY(BlueprintReadOnly, Category = "Statistics")
	int32 RareCardsPulled;

	// Show completion
	UFUNCTION()
	void OnShowCompleted(ACSVCardShow* CompletedShow);

	// Delegates
	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnReputationChanged OnReputationChanged;

	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnDayChanged OnDayChanged;

	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnShowCompleted OnShowCompletedDelegate;

	// Tier thresholds
	UPROPERTY(EditDefaultsOnly, Category = "Progression")
	TArray<int32> TierReputationThresholds;

	UPROPERTY(EditDefaultsOnly, Category = "Progression")
	TArray<FString> VendorRankNames;

protected:
	void InitializeDefaults();
};
