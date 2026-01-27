// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CSVCardTypes.h"
#include "CSVCardInstance.generated.h"

class UCSVCardData;

UCLASS(BlueprintType)
class CARDSHOWVENDOR_API UCSVCardInstance : public UObject
{
	GENERATED_BODY()

public:
	UCSVCardInstance();

	UFUNCTION(BlueprintCallable, Category = "Card")
	void InitializeFromData(UCSVCardData* Data);

	// Core data accessors
	UFUNCTION(BlueprintPure, Category = "Card")
	UCSVCardData* GetCardData() const { return CardData; }

	UFUNCTION(BlueprintPure, Category = "Card")
	FText GetCardName() const;

	UFUNCTION(BlueprintPure, Category = "Card")
	FName GetSport() const;

	UFUNCTION(BlueprintPure, Category = "Card")
	int32 GetRarity() const;

	// Value
	UFUNCTION(BlueprintPure, Category = "Card|Value")
	float GetBaseValue() const;

	UFUNCTION(BlueprintPure, Category = "Card|Value")
	float GetMarketValue() const;

	UFUNCTION(BlueprintPure, Category = "Card|Value")
	float GetListedPrice() const { return ListedPrice; }

	UFUNCTION(BlueprintCallable, Category = "Card|Value")
	void SetListedPrice(float Price) { ListedPrice = Price; }

	// Condition
	UFUNCTION(BlueprintPure, Category = "Card|Condition")
	ECSVCardCondition GetCondition() const { return Condition; }

	UFUNCTION(BlueprintCallable, Category = "Card|Condition")
	void SetCondition(ECSVCardCondition NewCondition) { Condition = NewCondition; }

	UFUNCTION(BlueprintPure, Category = "Card|Condition")
	float GetConditionMultiplier() const;

	// Grading
	UFUNCTION(BlueprintPure, Category = "Card|Grading")
	bool IsGraded() const { return Grade.IsGraded(); }

	UFUNCTION(BlueprintPure, Category = "Card|Grading")
	FCSVCardGrade GetGrade() const { return Grade; }

	UFUNCTION(BlueprintCallable, Category = "Card|Grading")
	void SetGrade(const FCSVCardGrade& NewGrade) { Grade = NewGrade; }

	UFUNCTION(BlueprintPure, Category = "Card|Grading")
	float GetGradeMultiplier() const { return Grade.GetGradeMultiplier(); }

	// Serial number (for numbered cards)
	UFUNCTION(BlueprintPure, Category = "Card|Serial")
	bool HasSerialNumber() const { return SerialNumber > 0; }

	UFUNCTION(BlueprintPure, Category = "Card|Serial")
	int32 GetSerialNumber() const { return SerialNumber; }

	UFUNCTION(BlueprintPure, Category = "Card|Serial")
	int32 GetTotalPrintRun() const;

	UFUNCTION(BlueprintCallable, Category = "Card|Serial")
	void SetSerialNumber(int32 Number) { SerialNumber = Number; }

	// Display
	UPROPERTY(BlueprintReadOnly, Category = "Card")
	bool bIsOnDisplay = false;

	UPROPERTY(BlueprintReadOnly, Category = "Card")
	int32 DisplaySlotIndex = -1;

protected:
	UPROPERTY()
	UCSVCardData* CardData;

	UPROPERTY()
	float ListedPrice;

	UPROPERTY()
	ECSVCardCondition Condition;

	UPROPERTY()
	FCSVCardGrade Grade;

	UPROPERTY()
	int32 SerialNumber;

	UPROPERTY()
	FGuid UniqueInstanceID;
};
