// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CSVDisplayCase.generated.h"

class UCSVCardInstance;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCardPlaced, UCSVCardInstance*, Card, int32, SlotIndex);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCardRemoved, UCSVCardInstance*, Card, int32, SlotIndex);

/**
 * Display case for showing cards to customers
 * Cards placed here are visible and available for purchase
 */
UCLASS()
class CARDSHOWVENDOR_API ACSVDisplayCase : public AActor
{
	GENERATED_BODY()

public:
	ACSVDisplayCase();

	virtual void BeginPlay() override;

	// Display slots
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display")
	int32 MaxSlots = 8;

	UPROPERTY(BlueprintReadOnly, Category = "Display")
	TArray<UCSVCardInstance*> CardSlots;

	// Case properties
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display")
	FName CaseType; // Basic, Premium, Vintage, etc.

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Display")
	float PrestigeBonus = 1.0f; // Affects card perceived value

	// Card management
	UFUNCTION(BlueprintCallable, Category = "Cards")
	bool PlaceCard(UCSVCardInstance* Card, int32 SlotIndex = -1);

	UFUNCTION(BlueprintCallable, Category = "Cards")
	UCSVCardInstance* RemoveCard(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "Cards")
	void ClearAllCards();

	UFUNCTION(BlueprintPure, Category = "Cards")
	UCSVCardInstance* GetCardInSlot(int32 SlotIndex) const;

	UFUNCTION(BlueprintPure, Category = "Cards")
	bool IsSlotEmpty(int32 SlotIndex) const;

	UFUNCTION(BlueprintPure, Category = "Cards")
	int32 GetFirstEmptySlot() const;

	UFUNCTION(BlueprintPure, Category = "Cards")
	TArray<UCSVCardInstance*> GetDisplayedCards() const;

	// Slot info
	UFUNCTION(BlueprintPure, Category = "Display")
	int32 GetMaxSlots() const { return MaxSlots; }

	UFUNCTION(BlueprintPure, Category = "Display")
	int32 GetUsedSlots() const;

	UFUNCTION(BlueprintPure, Category = "Display")
	bool HasEmptySlot() const { return GetFirstEmptySlot() != -1; }

	// Value calculation
	UFUNCTION(BlueprintPure, Category = "Value")
	float GetTotalDisplayValue() const;

	UFUNCTION(BlueprintPure, Category = "Value")
	float GetHighestCardValue() const;

	// Visual updates
	UFUNCTION(BlueprintCallable, Category = "Display")
	void RefreshDisplay();

	// Delegates
	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnCardPlaced OnCardPlaced;

	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnCardRemoved OnCardRemoved;

	// Components
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* RootSceneComponent;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* CaseMesh;

protected:
	// Card slot positions relative to case
	UPROPERTY(EditAnywhere, Category = "Layout")
	TArray<FVector> SlotPositions;

	void InitializeSlots();
};
