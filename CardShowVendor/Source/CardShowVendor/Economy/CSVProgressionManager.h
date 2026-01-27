// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CSVProgressionManager.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnLevelUp, int32, NewLevel, int32, NewTier);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnReputationChanged, int32, NewReputation, int32, Change);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAchievementUnlocked, FName, AchievementID);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnMilestoneReached, FName, MilestoneID);

USTRUCT(BlueprintType)
struct FCSVAchievement
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName AchievementID;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText AchievementName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText Description;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 ReputationReward = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float MoneyReward = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bUnlocked = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float Progress = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float RequiredProgress = 1.0f;
};

USTRUCT(BlueprintType)
struct FCSVVendorStats
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite)
	int32 TotalCardsSold = 0;

	UPROPERTY(BlueprintReadWrite)
	int32 TotalCardsBought = 0;

	UPROPERTY(BlueprintReadWrite)
	float TotalRevenue = 0.0f;

	UPROPERTY(BlueprintReadWrite)
	float TotalSpent = 0.0f;

	UPROPERTY(BlueprintReadWrite)
	int32 ShowsAttended = 0;

	UPROPERTY(BlueprintReadWrite)
	int32 CustomersServed = 0;

	UPROPERTY(BlueprintReadWrite)
	float HighestSingleSale = 0.0f;

	UPROPERTY(BlueprintReadWrite)
	int32 RareCardsFound = 0;

	UPROPERTY(BlueprintReadWrite)
	int32 LegendaryCardsFound = 0;

	UPROPERTY(BlueprintReadWrite)
	int32 PacksOpened = 0;

	UPROPERTY(BlueprintReadWrite)
	float PlayTimeHours = 0.0f;
};

USTRUCT(BlueprintType)
struct FCSVTierRequirements
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 RequiredReputation = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 RequiredShowsAttended = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float RequiredTotalRevenue = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText TierName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText TierDescription;
};

UCLASS(Blueprintable, BlueprintType)
class CARDSHOWVENDOR_API UCSVProgressionManager : public UObject
{
	GENERATED_BODY()

public:
	UCSVProgressionManager();

	// Initialization
	UFUNCTION(BlueprintCallable, Category = "Progression")
	void Initialize();

	UFUNCTION(BlueprintCallable, Category = "Progression")
	void LoadProgression();

	UFUNCTION(BlueprintCallable, Category = "Progression")
	void SaveProgression();

	// Level and reputation
	UPROPERTY(BlueprintReadOnly, Category = "Progression")
	int32 CurrentLevel;

	UPROPERTY(BlueprintReadOnly, Category = "Progression")
	int32 CurrentTier;

	UPROPERTY(BlueprintReadOnly, Category = "Progression")
	int32 CurrentReputation;

	UPROPERTY(BlueprintReadOnly, Category = "Progression")
	int32 ReputationToNextLevel;

	UFUNCTION(BlueprintCallable, Category = "Progression")
	void AddReputation(int32 Amount);

	UFUNCTION(BlueprintCallable, Category = "Progression")
	bool CanAccessTier(int32 Tier) const;

	UFUNCTION(BlueprintPure, Category = "Progression")
	float GetLevelProgress() const;

	UFUNCTION(BlueprintPure, Category = "Progression")
	int32 GetMaxAccessibleShowTier() const { return CurrentTier; }

	// Statistics
	UPROPERTY(BlueprintReadOnly, Category = "Statistics")
	FCSVVendorStats Stats;

	UFUNCTION(BlueprintCallable, Category = "Statistics")
	void RecordSale(float Amount, int32 CardRarity);

	UFUNCTION(BlueprintCallable, Category = "Statistics")
	void RecordPurchase(float Amount);

	UFUNCTION(BlueprintCallable, Category = "Statistics")
	void RecordShowAttended();

	UFUNCTION(BlueprintCallable, Category = "Statistics")
	void RecordCustomerServed();

	UFUNCTION(BlueprintCallable, Category = "Statistics")
	void RecordPackOpened(int32 RaresFound, int32 LegendariesFound);

	UFUNCTION(BlueprintCallable, Category = "Statistics")
	void UpdatePlayTime(float DeltaHours);

	// Achievements
	UFUNCTION(BlueprintCallable, Category = "Achievements")
	void CheckAchievements();

	UFUNCTION(BlueprintCallable, Category = "Achievements")
	void UnlockAchievement(FName AchievementID);

	UFUNCTION(BlueprintPure, Category = "Achievements")
	bool IsAchievementUnlocked(FName AchievementID) const;

	UFUNCTION(BlueprintPure, Category = "Achievements")
	TArray<FCSVAchievement> GetAllAchievements() const { return Achievements; }

	UFUNCTION(BlueprintPure, Category = "Achievements")
	TArray<FCSVAchievement> GetUnlockedAchievements() const;

	// Unlocks
	UFUNCTION(BlueprintPure, Category = "Progression")
	TArray<FName> GetUnlockedFeatures() const { return UnlockedFeatures; }

	UFUNCTION(BlueprintCallable, Category = "Progression")
	void UnlockFeature(FName FeatureID);

	UFUNCTION(BlueprintPure, Category = "Progression")
	bool IsFeatureUnlocked(FName FeatureID) const;

	// Delegates
	UPROPERTY(BlueprintAssignable, Category = "Progression|Events")
	FOnLevelUp OnLevelUp;

	UPROPERTY(BlueprintAssignable, Category = "Progression|Events")
	FOnReputationChanged OnReputationChanged;

	UPROPERTY(BlueprintAssignable, Category = "Progression|Events")
	FOnAchievementUnlocked OnAchievementUnlocked;

	UPROPERTY(BlueprintAssignable, Category = "Progression|Events")
	FOnMilestoneReached OnMilestoneReached;

protected:
	UPROPERTY()
	TArray<FCSVAchievement> Achievements;

	UPROPERTY()
	TArray<FCSVTierRequirements> TierRequirements;

	UPROPERTY()
	TArray<FName> UnlockedFeatures;

	void InitializeAchievements();
	void InitializeTierRequirements();
	void CheckLevelUp();
	void CheckTierUp();
	int32 CalculateReputationForLevel(int32 Level) const;
};
