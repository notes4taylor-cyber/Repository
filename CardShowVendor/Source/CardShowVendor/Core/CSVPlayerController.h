// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "CSVPlayerController.generated.h"

class UCSVMainHUD;
class UCSVCardInstance;
class ACSVVendorBooth;

UCLASS()
class CARDSHOWVENDOR_API ACSVPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	ACSVPlayerController();

	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;

	// UI
	UFUNCTION(BlueprintCallable, Category = "UI")
	void ShowMainHUD();

	UFUNCTION(BlueprintCallable, Category = "UI")
	void HideMainHUD();

	UFUNCTION(BlueprintCallable, Category = "UI")
	void OpenInventory();

	UFUNCTION(BlueprintCallable, Category = "UI")
	void CloseInventory();

	UFUNCTION(BlueprintCallable, Category = "UI")
	void OpenBoothManagement();

	UFUNCTION(BlueprintCallable, Category = "UI")
	void OpenMarketView();

	UFUNCTION(BlueprintCallable, Category = "UI")
	void OpenPackOpening();

	// Interaction
	UFUNCTION(BlueprintCallable, Category = "Interaction")
	void InteractWithBooth(ACSVVendorBooth* Booth);

	UFUNCTION(BlueprintCallable, Category = "Interaction")
	void SetCardPrice(UCSVCardInstance* Card, float NewPrice);

	UFUNCTION(BlueprintCallable, Category = "Interaction")
	void AddCardToDisplay(UCSVCardInstance* Card, int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "Interaction")
	void RemoveCardFromDisplay(int32 SlotIndex);

	// Transactions
	UFUNCTION(BlueprintCallable, Category = "Transactions")
	bool BuyPack(FName PackName);

	UFUNCTION(BlueprintCallable, Category = "Transactions")
	bool SellCard(UCSVCardInstance* Card, float Price);

	UFUNCTION(BlueprintCallable, Category = "Transactions")
	bool BuyCard(UCSVCardInstance* Card, float Price);

protected:
	UPROPERTY(EditDefaultsOnly, Category = "UI")
	TSubclassOf<UCSVMainHUD> MainHUDClass;

	UPROPERTY()
	UCSVMainHUD* MainHUDWidget;

	UPROPERTY()
	ACSVVendorBooth* CurrentBooth;

	// Input actions
	void OnPausePressed();
	void OnInventoryPressed();
	void OnInteractPressed();
};
