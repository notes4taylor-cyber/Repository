// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "CSVCardTypes.h"
#include "CSVCardData.generated.h"

UCLASS(BlueprintType)
class CARDSHOWVENDOR_API UCSVCardData : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UCSVCardData();

	// Identification
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	FName CardID;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	FText CardName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	FText CardNumber;

	// Player/Character Info
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	FText PlayerName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	FText TeamName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	int32 Year;

	// Set Info
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	FText SetName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	FText Manufacturer;

	// Classification
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	ECSVCardSport Sport;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	ECSVCardRarity Rarity;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card")
	ECSVCardEra Era;

	// Value
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Value")
	float BaseValue;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Value")
	float SpawnWeight = 1.0f;

	// Visuals
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Visual")
	TSoftObjectPtr<UTexture2D> CardFrontImage;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Visual")
	TSoftObjectPtr<UTexture2D> CardBackImage;

	// Special attributes
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Special")
	bool bIsRookieCard = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Special")
	bool bIsAutographed = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Special")
	bool bIsParallel = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Special")
	FText ParallelType;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Special")
	bool bIsNumbered = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Card|Special")
	int32 TotalPrintRun = 0;

	// Data asset functions
	virtual FPrimaryAssetId GetPrimaryAssetId() const override;
};
