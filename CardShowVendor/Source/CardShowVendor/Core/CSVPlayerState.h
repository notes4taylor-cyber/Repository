// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerState.h"
#include "CSVPlayerState.generated.h"

class UCSVCardInstance;
class UCSVCardData;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnMoneyChanged, float, NewAmount);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnInventoryChanged, int32, NewCount);

UCLASS()
class CARDSHOWVENDOR_API ACSVPlayerState : public APlayerState
{
	GENERATED_BODY()

public:
	ACSVPlayerState();

	virtual void BeginPlay() override;

	// Money management
	UPROPERTY(BlueprintReadOnly, Category = "Player")
	float Money;

	UFUNCTION(BlueprintCallable, Category = "Player|Money")
	void AddMoney(float Amount);

	UFUNCTION(BlueprintCallable, Category = "Player|Money")
	bool SpendMoney(float Amount);

	UFUNCTION(BlueprintPure, Category = "Player|Money")
	float GetMoney() const { return Money; }

	UFUNCTION(BlueprintPure, Category = "Player|Money")
	bool CanAfford(float Amount) const { return Money >= Amount; }

	// Inventory
	UPROPERTY(BlueprintReadOnly, Category = "Player")
	TArray<UCSVCardInstance*> CardInventory;

	UFUNCTION(BlueprintCallable, Category = "Player|Inventory")
	bool AddCardToInventory(UCSVCardInstance* Card);

	UFUNCTION(BlueprintCallable, Category = "Player|Inventory")
	bool RemoveCardFromInventory(UCSVCardInstance* Card);

	UFUNCTION(BlueprintPure, Category = "Player|Inventory")
	int32 GetInventoryCount() const { return CardInventory.Num(); }

	UFUNCTION(BlueprintPure, Category = "Player|Inventory")
	int32 GetMaxInventoryCapacity() const { return MaxInventoryCapacity; }

	UFUNCTION(BlueprintPure, Category = "Player|Inventory")
	bool HasInventorySpace() const { return CardInventory.Num() < MaxInventoryCapacity; }

	UFUNCTION(BlueprintCallable, Category = "Player|Inventory")
	TArray<UCSVCardInstance*> GetCardsByRarity(int32 Rarity) const;

	UFUNCTION(BlueprintCallable, Category = "Player|Inventory")
	TArray<UCSVCardInstance*> GetCardsBySport(FName Sport) const;

	UFUNCTION(BlueprintCallable, Category = "Player|Inventory")
	void SortInventoryByValue(bool bDescending = true);

	UFUNCTION(BlueprintCallable, Category = "Player|Inventory")
	UCSVCardInstance* CreateCardInstance(UCSVCardData* CardData);

	// Booth
	UPROPERTY(BlueprintReadOnly, Category = "Player")
	int32 BoothLevel;

	UPROPERTY(BlueprintReadOnly, Category = "Player")
	int32 DisplayCaseCount;

	// Features
	UFUNCTION(BlueprintCallable, Category = "Player|Features")
	bool UnlockFeature(FName FeatureName, float Cost);

	UFUNCTION(BlueprintPure, Category = "Player|Features")
	bool HasFeature(FName FeatureName) const;

	// Events
	UPROPERTY(BlueprintAssignable, Category = "Player|Events")
	FOnMoneyChanged OnMoneyChanged;

	UPROPERTY(BlueprintAssignable, Category = "Player|Events")
	FOnInventoryChanged OnInventoryChanged;

protected:
	UPROPERTY(EditDefaultsOnly, Category = "Player|Config")
	float StartingMoney = 100.0f;

	UPROPERTY(EditDefaultsOnly, Category = "Player|Config")
	int32 StartingBoothLevel = 1;

	UPROPERTY(EditDefaultsOnly, Category = "Player|Config")
	int32 StartingDisplayCases = 2;

	UPROPERTY(EditDefaultsOnly, Category = "Player|Config")
	int32 MaxInventoryCapacity = 100;

	UPROPERTY()
	TSet<FName> UnlockedFeatures;

	void InitializeStartingState();
};
