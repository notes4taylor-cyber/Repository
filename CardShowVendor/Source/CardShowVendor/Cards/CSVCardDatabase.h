// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CSVCardTypes.h"
#include "CSVCardDatabase.generated.h"

class UCSVCardData;
class UCSVCardInstance;

USTRUCT(BlueprintType)
struct FCSVPackConfiguration
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName PackName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 CardsPerPack = 10;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float PackPrice = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 GuaranteedRares = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	ECSVCardSport Sport;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TMap<ECSVCardRarity, float> RarityWeights;
};

UCLASS(Blueprintable, BlueprintType)
class CARDSHOWVENDOR_API UCSVCardDatabase : public UObject
{
	GENERATED_BODY()

public:
	UCSVCardDatabase();

	UFUNCTION(BlueprintCallable, Category = "Database")
	void InitializeDatabase();

	// Card queries
	UFUNCTION(BlueprintCallable, Category = "Database")
	TArray<UCSVCardData*> GetCardsBySport(ECSVCardSport Sport) const;

	UFUNCTION(BlueprintCallable, Category = "Database")
	TArray<UCSVCardData*> GetCardsByRarity(ECSVCardRarity Rarity) const;

	UFUNCTION(BlueprintCallable, Category = "Database")
	TArray<UCSVCardData*> GetCardsByEra(ECSVCardEra Era) const;

	UFUNCTION(BlueprintCallable, Category = "Database")
	UCSVCardData* GetCardByID(FName CardID) const;

	UFUNCTION(BlueprintCallable, Category = "Database")
	UCSVCardData* GetRandomCard(ECSVCardSport Sport = ECSVCardSport::Baseball) const;

	UFUNCTION(BlueprintCallable, Category = "Database")
	UCSVCardData* GetRandomCardByRarity(ECSVCardRarity Rarity) const;

	UFUNCTION(BlueprintPure, Category = "Database")
	int32 GetTotalCardCount() const { return RegisteredCards.Num(); }

	UFUNCTION(BlueprintPure, Category = "Database")
	int32 GetCardCountBySport(ECSVCardSport Sport) const;

	// Instance generation
	UFUNCTION(BlueprintCallable, Category = "Database")
	UCSVCardInstance* GenerateCardInstance(UCSVCardData* CardData, UObject* Outer = nullptr);

	UFUNCTION(BlueprintCallable, Category = "Database")
	UCSVCardInstance* GenerateRandomCardInstance(ECSVCardSport Sport, UObject* Outer = nullptr);

	// Pack operations
	UFUNCTION(BlueprintCallable, Category = "Database|Packs")
	TArray<UCSVCardInstance*> OpenPack(const FCSVPackConfiguration& PackConfig, UObject* Outer = nullptr);

	UFUNCTION(BlueprintPure, Category = "Database|Packs")
	TArray<FCSVPackConfiguration> GetAvailablePacks() const { return AvailablePacks; }

	UFUNCTION(BlueprintPure, Category = "Database|Packs")
	FCSVPackConfiguration GetPackByName(FName PackName) const;

protected:
	UPROPERTY()
	TArray<UCSVCardData*> RegisteredCards;

	UPROPERTY()
	TMap<ECSVCardSport, TArray<UCSVCardData*>> CardsBySport;

	UPROPERTY()
	TMap<ECSVCardRarity, TArray<UCSVCardData*>> CardsByRarity;

	UPROPERTY()
	TArray<FCSVPackConfiguration> AvailablePacks;

	void GenerateDefaultCards();
	void BuildCaches();
	ECSVCardRarity RollRarity(const TMap<ECSVCardRarity, float>& Weights) const;

	UCSVCardData* CreateRuntimeCardData(
		FName ID,
		const FString& PlayerName,
		const FString& Team,
		int32 Year,
		const FString& SetName,
		ECSVCardSport Sport,
		ECSVCardRarity Rarity,
		float BaseValue,
		int32 CardNumber);
};
