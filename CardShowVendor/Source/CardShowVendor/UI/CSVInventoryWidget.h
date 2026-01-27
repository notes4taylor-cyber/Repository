// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "CSVInventoryWidget.generated.h"

class UCSVCardInstance;
class UScrollBox;
class UWrapBox;
class UTextBlock;
class UButton;
class UComboBoxString;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCardSelected, UCSVCardInstance*, Card);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCardPriceSet, UCSVCardInstance*, Card, float, Price);

UENUM(BlueprintType)
enum class ECSVInventorySortMode : uint8
{
	ByName,
	ByValue,
	ByRarity,
	BySport,
	ByRecent
};

UCLASS()
class CARDSHOWVENDOR_API UCSVInventoryWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	virtual void NativeConstruct() override;

	UFUNCTION(BlueprintCallable, Category = "Inventory")
	void RefreshInventory(const TArray<UCSVCardInstance*>& Cards);

	UFUNCTION(BlueprintCallable, Category = "Inventory")
	void SetSortMode(ECSVInventorySortMode Mode);

	UFUNCTION(BlueprintCallable, Category = "Inventory")
	void SetFilter(FName SportFilter, int32 RarityFilter);

	UFUNCTION(BlueprintCallable, Category = "Inventory")
	void ClearFilters();

	UFUNCTION(BlueprintCallable, Category = "Inventory")
	void SelectCard(UCSVCardInstance* Card);

	UFUNCTION(BlueprintPure, Category = "Inventory")
	UCSVCardInstance* GetSelectedCard() const { return SelectedCard; }

	UPROPERTY(BlueprintAssignable, Category = "Inventory|Events")
	FOnCardSelected OnCardSelected;

	UPROPERTY(BlueprintAssignable, Category = "Inventory|Events")
	FOnCardPriceSet OnCardPriceSet;

protected:
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UWrapBox* CardGridBox;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* InventoryValueText;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* CardCountText;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UComboBoxString* SortDropdown;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UComboBoxString* SportFilterDropdown;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UComboBoxString* RarityFilterDropdown;

	// Selected card details
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* SelectedCardName;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* SelectedCardValue;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* SelectedCardRarity;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UButton* SetPriceButton;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UButton* AddToDisplayButton;

	UPROPERTY(EditDefaultsOnly, Category = "Inventory")
	TSubclassOf<UUserWidget> CardEntryWidgetClass;

private:
	UPROPERTY()
	TArray<UCSVCardInstance*> CurrentInventory;

	UPROPERTY()
	TArray<UCSVCardInstance*> FilteredInventory;

	UPROPERTY()
	UCSVCardInstance* SelectedCard;

	UPROPERTY()
	ECSVInventorySortMode CurrentSortMode;

	UPROPERTY()
	FName CurrentSportFilter;

	UPROPERTY()
	int32 CurrentRarityFilter;

	void ApplyFiltersAndSort();
	void UpdateCardGrid();
	void UpdateSelectedCardDisplay();
	float CalculateTotalInventoryValue() const;
};
