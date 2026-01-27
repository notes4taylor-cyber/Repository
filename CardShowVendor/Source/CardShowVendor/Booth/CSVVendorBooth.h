// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CSVVendorBooth.generated.h"

class UCSVCardInstance;
class UStaticMeshComponent;
class UBoxComponent;

USTRUCT(BlueprintType)
struct FCSVDisplaySlot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly)
	int32 SlotIndex = -1;

	UPROPERTY(BlueprintReadOnly)
	UCSVCardInstance* DisplayedCard = nullptr;

	UPROPERTY(BlueprintReadOnly)
	FVector LocalPosition = FVector::ZeroVector;

	UPROPERTY(BlueprintReadOnly)
	bool bIsHighlighted = false;
};

USTRUCT(BlueprintType)
struct FCSVBoothStats
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly)
	int32 SalesThisShow = 0;

	UPROPERTY(BlueprintReadOnly)
	float RevenueThisShow = 0.0f;

	UPROPERTY(BlueprintReadOnly)
	int32 CustomersVisited = 0;

	UPROPERTY(BlueprintReadOnly)
	float HighestSale = 0.0f;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCardSold, UCSVCardInstance*, Card, float, Price);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCustomerApproached, AActor*, Customer);

UCLASS()
class CARDSHOWVENDOR_API ACSVVendorBooth : public AActor
{
	GENERATED_BODY()

public:
	ACSVVendorBooth();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	// Booth setup
	UFUNCTION(BlueprintCallable, Category = "Booth")
	void InitializeBooth(int32 BoothLevel);

	UFUNCTION(BlueprintCallable, Category = "Booth")
	void UpgradeBooth();

	// Display management
	UFUNCTION(BlueprintCallable, Category = "Booth|Display")
	bool AddCardToDisplay(UCSVCardInstance* Card, int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "Booth|Display")
	UCSVCardInstance* RemoveCardFromDisplay(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "Booth|Display")
	void ClearAllDisplays();

	UFUNCTION(BlueprintPure, Category = "Booth|Display")
	int32 GetDisplaySlotCount() const { return DisplaySlots.Num(); }

	UFUNCTION(BlueprintPure, Category = "Booth|Display")
	TArray<FCSVDisplaySlot> GetDisplaySlots() const { return DisplaySlots; }

	UFUNCTION(BlueprintPure, Category = "Booth|Display")
	UCSVCardInstance* GetCardInSlot(int32 SlotIndex) const;

	UFUNCTION(BlueprintPure, Category = "Booth|Display")
	TArray<UCSVCardInstance*> GetAllDisplayedCards() const;

	// Sales
	UFUNCTION(BlueprintCallable, Category = "Booth|Sales")
	bool SellCard(UCSVCardInstance* Card, float Price);

	UFUNCTION(BlueprintCallable, Category = "Booth|Sales")
	void RecordSale(float Amount);

	// Stats
	UFUNCTION(BlueprintPure, Category = "Booth|Stats")
	FCSVBoothStats GetBoothStats() const { return Stats; }

	UFUNCTION(BlueprintCallable, Category = "Booth|Stats")
	void ResetShowStats();

	// Properties
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Booth")
	int32 CurrentLevel = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Booth")
	FText BoothName;

	// Events
	UPROPERTY(BlueprintAssignable, Category = "Booth|Events")
	FOnCardSold OnCardSold;

	UPROPERTY(BlueprintAssignable, Category = "Booth|Events")
	FOnCustomerApproached OnCustomerApproached;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* BoothMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UBoxComponent* InteractionVolume;

	UPROPERTY()
	TArray<FCSVDisplaySlot> DisplaySlots;

	UPROPERTY()
	FCSVBoothStats Stats;

	void SetupDisplaySlots(int32 SlotCount);

	UFUNCTION()
	void OnInteractionBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, 
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);
};
