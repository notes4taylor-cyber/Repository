// Copyright Card Show Vendor. All Rights Reserved.

#include "UI/CSVInventoryWidget.h"
#include "Cards/CSVCardInstance.h"
#include "Components/WrapBox.h"
#include "Components/TextBlock.h"
#include "Components/Button.h"
#include "Components/ComboBoxString.h"
#include "CardShowVendor.h"

void UCSVInventoryWidget::NativeConstruct()
{
	Super::NativeConstruct();

	CurrentSortMode = ECSVInventorySortMode::ByValue;
	CurrentRarityFilter = -1; // No filter
	SelectedCard = nullptr;

	// Setup sort dropdown
	if (SortDropdown)
	{
		SortDropdown->AddOption(TEXT("By Name"));
		SortDropdown->AddOption(TEXT("By Value"));
		SortDropdown->AddOption(TEXT("By Rarity"));
		SortDropdown->AddOption(TEXT("By Sport"));
		SortDropdown->AddOption(TEXT("By Recent"));
		SortDropdown->SetSelectedIndex(1); // Default to By Value
	}

	// Setup sport filter dropdown
	if (SportFilterDropdown)
	{
		SportFilterDropdown->AddOption(TEXT("All Sports"));
		SportFilterDropdown->AddOption(TEXT("Baseball"));
		SportFilterDropdown->AddOption(TEXT("Basketball"));
		SportFilterDropdown->AddOption(TEXT("Football"));
		SportFilterDropdown->AddOption(TEXT("Pokemon"));
		SportFilterDropdown->AddOption(TEXT("Magic: The Gathering"));
		SportFilterDropdown->SetSelectedIndex(0);
	}

	// Setup rarity filter dropdown
	if (RarityFilterDropdown)
	{
		RarityFilterDropdown->AddOption(TEXT("All Rarities"));
		RarityFilterDropdown->AddOption(TEXT("Common"));
		RarityFilterDropdown->AddOption(TEXT("Uncommon"));
		RarityFilterDropdown->AddOption(TEXT("Rare"));
		RarityFilterDropdown->AddOption(TEXT("Ultra Rare"));
		RarityFilterDropdown->AddOption(TEXT("Legendary"));
		RarityFilterDropdown->SetSelectedIndex(0);
	}
}

void UCSVInventoryWidget::RefreshInventory(const TArray<UCSVCardInstance*>& Cards)
{
	CurrentInventory = Cards;
	ApplyFiltersAndSort();
	UpdateCardGrid();

	// Update totals
	if (CardCountText)
	{
		CardCountText->SetText(FText::FromString(
			FString::Printf(TEXT("%d Cards"), CurrentInventory.Num())));
	}

	if (InventoryValueText)
	{
		float TotalValue = CalculateTotalInventoryValue();
		InventoryValueText->SetText(FText::FromString(
			FString::Printf(TEXT("Total Value: $%.2f"), TotalValue)));
	}
}

void UCSVInventoryWidget::SetSortMode(ECSVInventorySortMode Mode)
{
	CurrentSortMode = Mode;
	ApplyFiltersAndSort();
	UpdateCardGrid();
}

void UCSVInventoryWidget::SetFilter(FName SportFilter, int32 RarityFilter)
{
	CurrentSportFilter = SportFilter;
	CurrentRarityFilter = RarityFilter;
	ApplyFiltersAndSort();
	UpdateCardGrid();
}

void UCSVInventoryWidget::ClearFilters()
{
	CurrentSportFilter = NAME_None;
	CurrentRarityFilter = -1;
	ApplyFiltersAndSort();
	UpdateCardGrid();
}

void UCSVInventoryWidget::SelectCard(UCSVCardInstance* Card)
{
	SelectedCard = Card;
	UpdateSelectedCardDisplay();
	OnCardSelected.Broadcast(Card);
}

void UCSVInventoryWidget::ApplyFiltersAndSort()
{
	FilteredInventory.Empty();

	// Apply filters
	for (UCSVCardInstance* Card : CurrentInventory)
	{
		if (!Card) continue;

		// Sport filter
		if (CurrentSportFilter != NAME_None)
		{
			if (Card->GetSport() != CurrentSportFilter)
			{
				continue;
			}
		}

		// Rarity filter
		if (CurrentRarityFilter >= 0)
		{
			if (Card->GetRarity() != CurrentRarityFilter)
			{
				continue;
			}
		}

		FilteredInventory.Add(Card);
	}

	// Apply sort
	switch (CurrentSortMode)
	{
	case ECSVInventorySortMode::ByName:
		FilteredInventory.Sort([](const UCSVCardInstance& A, const UCSVCardInstance& B)
		{
			return A.GetCardName().ToString() < B.GetCardName().ToString();
		});
		break;

	case ECSVInventorySortMode::ByValue:
		FilteredInventory.Sort([](const UCSVCardInstance& A, const UCSVCardInstance& B)
		{
			return A.GetMarketValue() > B.GetMarketValue();
		});
		break;

	case ECSVInventorySortMode::ByRarity:
		FilteredInventory.Sort([](const UCSVCardInstance& A, const UCSVCardInstance& B)
		{
			return A.GetRarity() > B.GetRarity();
		});
		break;

	case ECSVInventorySortMode::BySport:
		FilteredInventory.Sort([](const UCSVCardInstance& A, const UCSVCardInstance& B)
		{
			return A.GetSport().ToString() < B.GetSport().ToString();
		});
		break;

	case ECSVInventorySortMode::ByRecent:
		// Keep original order (most recent first)
		break;
	}
}

void UCSVInventoryWidget::UpdateCardGrid()
{
	if (!CardGridBox)
	{
		return;
	}

	CardGridBox->ClearChildren();

	// In a full implementation, this would create card entry widgets
	// For now, we'll just log the update
	UE_LOG(LogCardShowVendor, Verbose, TEXT("Inventory grid updated with %d filtered cards"),
		FilteredInventory.Num());
}

void UCSVInventoryWidget::UpdateSelectedCardDisplay()
{
	if (!SelectedCard)
	{
		if (SelectedCardName) SelectedCardName->SetText(FText::FromString(TEXT("No card selected")));
		if (SelectedCardValue) SelectedCardValue->SetText(FText::GetEmpty());
		if (SelectedCardRarity) SelectedCardRarity->SetText(FText::GetEmpty());
		return;
	}

	if (SelectedCardName)
	{
		SelectedCardName->SetText(SelectedCard->GetCardName());
	}

	if (SelectedCardValue)
	{
		SelectedCardValue->SetText(FText::FromString(
			FString::Printf(TEXT("Market Value: $%.2f"), SelectedCard->GetMarketValue())));
	}

	if (SelectedCardRarity)
	{
		TArray<FString> RarityNames = {
			TEXT("Common"), TEXT("Uncommon"), TEXT("Rare"),
			TEXT("Ultra Rare"), TEXT("Legendary"), TEXT("One of One")
		};
		int32 Rarity = SelectedCard->GetRarity();
		FString RarityName = RarityNames.IsValidIndex(Rarity) ? RarityNames[Rarity] : TEXT("Unknown");
		SelectedCardRarity->SetText(FText::FromString(RarityName));
	}
}

float UCSVInventoryWidget::CalculateTotalInventoryValue() const
{
	float Total = 0.0f;
	for (const UCSVCardInstance* Card : CurrentInventory)
	{
		if (Card)
		{
			Total += Card->GetMarketValue();
		}
	}
	return Total;
}
