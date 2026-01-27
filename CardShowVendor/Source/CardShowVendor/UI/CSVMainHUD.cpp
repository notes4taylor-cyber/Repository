// Copyright Card Show Vendor. All Rights Reserved.

#include "UI/CSVMainHUD.h"
#include "Components/TextBlock.h"
#include "Components/ProgressBar.h"
#include "Components/VerticalBox.h"
#include "Components/Button.h"
#include "CardShowVendor.h"

void UCSVMainHUD::NativeConstruct()
{
	Super::NativeConstruct();

	// Initialize displays
	UpdateMoney(0.0f);
	UpdateReputation(0, 1, 0);
	UpdateInventoryCount(0, 100);
	UpdateCustomerQueue(0);
}

void UCSVMainHUD::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	ClearExpiredNotifications(InDeltaTime);
}

void UCSVMainHUD::UpdateMoney(float NewAmount)
{
	if (MoneyText)
	{
		FString MoneyString = FString::Printf(TEXT("$%.2f"), NewAmount);
		MoneyText->SetText(FText::FromString(MoneyString));
	}
}

void UCSVMainHUD::UpdateReputation(int32 NewReputation, int32 Level, int32 Tier)
{
	if (LevelText)
	{
		LevelText->SetText(FText::FromString(FString::Printf(TEXT("Level %d"), Level)));
	}

	if (TierText)
	{
		TArray<FString> TierNames = {
			TEXT("Beginner"),
			TEXT("Amateur"),
			TEXT("Established"),
			TEXT("Professional"),
			TEXT("Expert"),
			TEXT("Elite")
		};
		FString TierName = TierNames.IsValidIndex(Tier) ? TierNames[Tier] : TEXT("Unknown");
		TierText->SetText(FText::FromString(TierName));
	}

	// Calculate progress to next level (simplified)
	if (ReputationProgressBar)
	{
		float Progress = FMath::Fmod((float)NewReputation, 100.0f) / 100.0f;
		ReputationProgressBar->SetPercent(Progress);
	}
}

void UCSVMainHUD::UpdateInventoryCount(int32 Count, int32 MaxCapacity)
{
	if (InventoryCountText)
	{
		InventoryCountText->SetText(FText::FromString(
			FString::Printf(TEXT("%d / %d Cards"), Count, MaxCapacity)));
	}

	if (InventoryCapacityBar)
	{
		float Percent = MaxCapacity > 0 ? (float)Count / MaxCapacity : 0.0f;
		InventoryCapacityBar->SetPercent(Percent);
	}
}

void UCSVMainHUD::UpdateShowInfo(const FText& ShowName, float Progress, float RemainingTime)
{
	if (ShowNameText)
	{
		ShowNameText->SetText(ShowName);
	}

	if (ShowProgressBar)
	{
		ShowProgressBar->SetPercent(Progress);
	}

	if (ShowTimeText)
	{
		int32 Hours = FMath::FloorToInt(RemainingTime / 3600.0f);
		int32 Minutes = FMath::FloorToInt(FMath::Fmod(RemainingTime, 3600.0f) / 60.0f);
		ShowTimeText->SetText(FText::FromString(
			FString::Printf(TEXT("%dh %dm remaining"), Hours, Minutes)));
	}
}

void UCSVMainHUD::ShowNotification(const FText& Message, float Duration)
{
	if (NotificationBox)
	{
		UTextBlock* NotificationText = NewObject<UTextBlock>(this);
		NotificationText->SetText(Message);
		NotificationText->SetColorAndOpacity(FSlateColor(FLinearColor::White));

		NotificationBox->AddChild(NotificationText);
		NotificationTimers.Add(Duration);
	}
}

void UCSVMainHUD::ShowAchievementPopup(const FText& AchievementName, int32 ReputationReward)
{
	FText Message = FText::FromString(FString::Printf(
		TEXT("Achievement Unlocked: %s (+%d Rep)"),
		*AchievementName.ToString(),
		ReputationReward));

	ShowNotification(Message, 5.0f);
}

void UCSVMainHUD::ShowMarketAlert(const FText& AlertMessage)
{
	FText Message = FText::FromString(FString::Printf(
		TEXT("[MARKET] %s"), *AlertMessage.ToString()));

	ShowNotification(Message, 4.0f);
}

void UCSVMainHUD::UpdateCustomerQueue(int32 WaitingCustomers)
{
	if (CustomerQueueText)
	{
		if (WaitingCustomers > 0)
		{
			CustomerQueueText->SetText(FText::FromString(
				FString::Printf(TEXT("%d customers browsing"), WaitingCustomers)));
		}
		else
		{
			CustomerQueueText->SetText(FText::FromString(TEXT("No customers")));
		}
	}
}

void UCSVMainHUD::ClearExpiredNotifications(float DeltaTime)
{
	if (!NotificationBox)
	{
		return;
	}

	for (int32 i = NotificationTimers.Num() - 1; i >= 0; --i)
	{
		NotificationTimers[i] -= DeltaTime;

		if (NotificationTimers[i] <= 0.0f)
		{
			if (NotificationBox->GetChildrenCount() > i)
			{
				NotificationBox->RemoveChildAt(i);
			}
			NotificationTimers.RemoveAt(i);
		}
	}
}
