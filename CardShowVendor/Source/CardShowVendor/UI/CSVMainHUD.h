// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "CSVMainHUD.generated.h"

class UCSVCardInstance;
class UTextBlock;
class UProgressBar;
class UVerticalBox;
class UButton;

UCLASS()
class CARDSHOWVENDOR_API UCSVMainHUD : public UUserWidget
{
	GENERATED_BODY()

public:
	virtual void NativeConstruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	// Update functions
	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdateMoney(float NewAmount);

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdateReputation(int32 NewReputation, int32 Level, int32 Tier);

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdateInventoryCount(int32 Count, int32 MaxCapacity);

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdateShowInfo(const FText& ShowName, float Progress, float RemainingTime);

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowNotification(const FText& Message, float Duration = 3.0f);

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowAchievementPopup(const FText& AchievementName, int32 ReputationReward);

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowMarketAlert(const FText& AlertMessage);

	UFUNCTION(BlueprintCallable, Category = "HUD")
	void UpdateCustomerQueue(int32 WaitingCustomers);

protected:
	// Money display
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* MoneyText;

	// Reputation/Level display
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* LevelText;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* TierText;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UProgressBar* ReputationProgressBar;

	// Inventory display
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* InventoryCountText;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UProgressBar* InventoryCapacityBar;

	// Show info
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* ShowNameText;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* ShowTimeText;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UProgressBar* ShowProgressBar;

	// Notifications
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UVerticalBox* NotificationBox;

	// Customer queue
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UTextBlock* CustomerQueueText;

	// Quick action buttons
	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UButton* InventoryButton;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UButton* BoothButton;

	UPROPERTY(meta = (BindWidget), BlueprintReadOnly)
	UButton* MarketButton;

private:
	UPROPERTY()
	TArray<float> NotificationTimers;

	void ClearExpiredNotifications(float DeltaTime);
};
