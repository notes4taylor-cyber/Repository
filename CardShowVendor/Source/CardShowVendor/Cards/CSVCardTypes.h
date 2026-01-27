// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "CSVCardTypes.generated.h"

UENUM(BlueprintType)
enum class ECSVCardRarity : uint8
{
	Common			UMETA(DisplayName = "Common"),
	Uncommon		UMETA(DisplayName = "Uncommon"),
	Rare			UMETA(DisplayName = "Rare"),
	UltraRare		UMETA(DisplayName = "Ultra Rare"),
	Legendary		UMETA(DisplayName = "Legendary"),
	OneOfOne		UMETA(DisplayName = "1/1")
};

UENUM(BlueprintType)
enum class ECSVCardSport : uint8
{
	Baseball		UMETA(DisplayName = "Baseball"),
	Basketball		UMETA(DisplayName = "Basketball"),
	Football		UMETA(DisplayName = "Football"),
	Hockey			UMETA(DisplayName = "Hockey"),
	Soccer			UMETA(DisplayName = "Soccer"),
	Pokemon			UMETA(DisplayName = "Pokemon"),
	MagicTheGathering	UMETA(DisplayName = "Magic: The Gathering"),
	YuGiOh			UMETA(DisplayName = "Yu-Gi-Oh!"),
	Other			UMETA(DisplayName = "Other")
};

UENUM(BlueprintType)
enum class ECSVCardEra : uint8
{
	Vintage			UMETA(DisplayName = "Vintage (Pre-1980)"),
	JunkWax			UMETA(DisplayName = "Junk Wax (1980-1994)"),
	Modern			UMETA(DisplayName = "Modern (1995-2009)"),
	Ultra_Modern	UMETA(DisplayName = "Ultra Modern (2010+)")
};

UENUM(BlueprintType)
enum class ECSVCardCondition : uint8
{
	Poor			UMETA(DisplayName = "Poor"),
	Fair			UMETA(DisplayName = "Fair"),
	Good			UMETA(DisplayName = "Good"),
	VeryGood		UMETA(DisplayName = "Very Good"),
	Excellent		UMETA(DisplayName = "Excellent"),
	NearMint		UMETA(DisplayName = "Near Mint"),
	Mint			UMETA(DisplayName = "Mint"),
	GemMint			UMETA(DisplayName = "Gem Mint")
};

USTRUCT(BlueprintType)
struct FCSVCardGrade
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName GradingCompany; // PSA, BGS, CGC, etc.

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float NumericGrade = 0.0f; // 1-10 scale

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FString CertificationNumber;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bIsAuthenticated = false;

	bool IsGraded() const { return NumericGrade > 0.0f; }

	float GetGradeMultiplier() const
	{
		if (NumericGrade >= 10.0f) return 5.0f;
		if (NumericGrade >= 9.5f) return 3.0f;
		if (NumericGrade >= 9.0f) return 2.0f;
		if (NumericGrade >= 8.0f) return 1.5f;
		if (NumericGrade >= 7.0f) return 1.2f;
		return 1.0f;
	}
};
