// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CSVCardShow.generated.h"

class ACSVVendorBooth;
class ACSVCustomer;

UENUM(BlueprintType)
enum class ECSVShowType : uint8
{
	LocalShow		UMETA(DisplayName = "Local Show"),
	RegionalShow	UMETA(DisplayName = "Regional Show"),
	NationalShow	UMETA(DisplayName = "National Show"),
	PremiumShow		UMETA(DisplayName = "Premium Showcase")
};

USTRUCT(BlueprintType)
struct FCSVShowConfig
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText ShowName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	ECSVShowType ShowType;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 RequiredTier = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float EntryCost = 50.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float CustomerSpawnRate = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float CustomerWealthMultiplier = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 MaxConcurrentCustomers = 10;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float ShowDurationHours = 8.0f;
};

UCLASS()
class CARDSHOWVENDOR_API ACSVCardShow : public AActor
{
	GENERATED_BODY()

public:
	ACSVCardShow();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	// Show management
	UFUNCTION(BlueprintCallable, Category = "Show")
	void InitializeShow(int32 Tier);

	UFUNCTION(BlueprintCallable, Category = "Show")
	void FinalizeShow();

	UFUNCTION(BlueprintCallable, Category = "Show")
	void SetPlayerBooth(ACSVVendorBooth* Booth);

	UFUNCTION(BlueprintPure, Category = "Show")
	bool IsShowActive() const { return bShowActive; }

	UFUNCTION(BlueprintPure, Category = "Show")
	FCSVShowConfig GetShowConfig() const { return ShowConfig; }

	UFUNCTION(BlueprintPure, Category = "Show")
	int32 GetShowTier() const { return ShowTier; }

	// Progress
	UFUNCTION(BlueprintPure, Category = "Show")
	float GetShowProgress() const;

	UFUNCTION(BlueprintPure, Category = "Show")
	float GetRemainingTime() const;

	// Customer management
	UFUNCTION(BlueprintCallable, Category = "Show|Customers")
	ACSVCustomer* SpawnCustomer();

	UFUNCTION(BlueprintCallable, Category = "Show|Customers")
	void DespawnCustomer(ACSVCustomer* Customer);

	UFUNCTION(BlueprintPure, Category = "Show|Customers")
	int32 GetActiveCustomerCount() const { return ActiveCustomers.Num(); }

	// Statistics
	UFUNCTION(BlueprintCallable, Category = "Show|Stats")
	void RecordSale(float Amount);

	UFUNCTION(BlueprintCallable, Category = "Show|Stats")
	void RecordCustomerServed(bool bMadePurchase);

	UFUNCTION(BlueprintPure, Category = "Show|Stats")
	int32 CalculateReputationGain() const;

	UPROPERTY(BlueprintReadOnly, Category = "Show|Stats")
	int32 CardsSoldThisShow;

	UPROPERTY(BlueprintReadOnly, Category = "Show|Stats")
	float RevenueThisShow;

	UPROPERTY(BlueprintReadOnly, Category = "Show|Stats")
	int32 CustomersServedThisShow;

	UPROPERTY(BlueprintReadOnly, Category = "Show|Stats")
	int32 CustomersLostThisShow;

	UPROPERTY(BlueprintReadOnly, Category = "Show|Stats")
	float HighestSingleSale;

protected:
	UPROPERTY()
	int32 ShowTier;

	UPROPERTY()
	FCSVShowConfig ShowConfig;

	UPROPERTY()
	bool bShowActive;

	UPROPERTY()
	float ShowElapsedTime;

	UPROPERTY()
	float CustomerSpawnTimer;

	UPROPERTY()
	ACSVVendorBooth* PlayerBooth;

	UPROPERTY()
	TArray<ACSVCustomer*> ActiveCustomers;

	UPROPERTY()
	TArray<FCSVShowConfig> ShowPresets;

	UPROPERTY(EditDefaultsOnly, Category = "Show")
	TSubclassOf<ACSVCustomer> CustomerClass;

	void InitializeShowPresets();
	FCSVShowConfig GetConfigForTier(int32 Tier) const;
	void UpdateCustomerSpawning(float DeltaTime);
};
