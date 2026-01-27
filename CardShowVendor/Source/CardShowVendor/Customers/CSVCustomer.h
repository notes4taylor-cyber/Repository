// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "CSVCustomer.generated.h"

class ACSVVendorBooth;
class UCSVCardInstance;

UENUM(BlueprintType)
enum class ECSVCustomerType : uint8
{
	Casual			UMETA(DisplayName = "Casual Collector"),
	Dedicated		UMETA(DisplayName = "Dedicated Collector"),
	Investor		UMETA(DisplayName = "Card Investor"),
	Flipper			UMETA(DisplayName = "Card Flipper"),
	Whale			UMETA(DisplayName = "Big Spender"),
	Newbie			UMETA(DisplayName = "New Collector")
};

UENUM(BlueprintType)
enum class ECSVCustomerState : uint8
{
	Wandering,
	ApproachingBooth,
	Browsing,
	Negotiating,
	Purchasing,
	Leaving
};

USTRUCT(BlueprintType)
struct FCSVCustomerPreferences
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<FName> PreferredSports;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<FName> PreferredTeams;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<FName> PreferredPlayers;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 MinRarityInterest = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 MaxRarityInterest = 5;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bPrefersVintage = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bPrefersModern = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bLookingForDeals = false;
};

UCLASS()
class CARDSHOWVENDOR_API ACSVCustomer : public ACharacter
{
	GENERATED_BODY()

public:
	ACSVCustomer();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	// Initialization
	UFUNCTION(BlueprintCallable, Category = "Customer")
	void InitializeCustomer(float WealthMultiplier = 1.0f);

	UFUNCTION(BlueprintCallable, Category = "Customer")
	void SetTargetBooth(ACSVVendorBooth* Booth);

	// Customer properties
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customer")
	ECSVCustomerType CustomerType;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Customer")
	ECSVCustomerState CurrentState;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customer")
	float Budget;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customer")
	float Patience;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customer")
	float HaggleSkill;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customer")
	float KnowledgeLevel;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Customer")
	FCSVCustomerPreferences Preferences;

	// Behavior
	UFUNCTION(BlueprintCallable, Category = "Customer|Behavior")
	void StartBrowsing();

	UFUNCTION(BlueprintCallable, Category = "Customer|Behavior")
	void StopBrowsing();

	UFUNCTION(BlueprintCallable, Category = "Customer|Behavior")
	bool IsInterestedInCard(UCSVCardInstance* Card) const;

	UFUNCTION(BlueprintCallable, Category = "Customer|Behavior")
	float CalculateWillingToPay(UCSVCardInstance* Card) const;

	UFUNCTION(BlueprintCallable, Category = "Customer|Behavior")
	bool AttemptPurchase(UCSVCardInstance* Card, float AskingPrice);

	UFUNCTION(BlueprintCallable, Category = "Customer|Behavior")
	float MakeCounterOffer(float AskingPrice, float PerceivedValue);

	UFUNCTION(BlueprintCallable, Category = "Customer|Behavior")
	void CompletePurchase(UCSVCardInstance* Card, float FinalPrice);

	UFUNCTION(BlueprintCallable, Category = "Customer|Behavior")
	void LeaveWithoutPurchase();

	// Getters
	UFUNCTION(BlueprintPure, Category = "Customer")
	float GetRemainingBudget() const { return Budget; }

	UFUNCTION(BlueprintPure, Category = "Customer")
	bool HasBudgetFor(float Amount) const { return Budget >= Amount; }

	UFUNCTION(BlueprintPure, Category = "Customer")
	ACSVVendorBooth* GetTargetBooth() const { return TargetBooth; }

protected:
	UPROPERTY()
	ACSVVendorBooth* TargetBooth;

	UPROPERTY()
	float BrowseTimer;

	UPROPERTY()
	float PatienceTimer;

	UPROPERTY()
	int32 CardsExamined;

	UPROPERTY()
	int32 OffersRejected;

	UPROPERTY()
	TArray<UCSVCardInstance*> InterestedCards;

	void UpdateBehavior(float DeltaTime);
	void GenerateRandomPreferences();
	void SetCustomerTypeDefaults();
};
