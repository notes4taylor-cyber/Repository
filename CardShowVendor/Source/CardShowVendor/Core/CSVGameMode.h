// Copyright Card Show Vendor. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "CSVGameMode.generated.h"

class UCSVCardDatabase;
class UCSVEconomyManager;
class UCSVProgressionManager;
class ACSVCardShow;

UCLASS()
class CARDSHOWVENDOR_API ACSVGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ACSVGameMode();

	virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
	virtual void StartPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	// Getters for subsystems
	UFUNCTION(BlueprintPure, Category = "Game")
	UCSVCardDatabase* GetCardDatabase() const { return CardDatabase; }

	UFUNCTION(BlueprintPure, Category = "Game")
	UCSVEconomyManager* GetEconomyManager() const { return EconomyManager; }

	UFUNCTION(BlueprintPure, Category = "Game")
	UCSVProgressionManager* GetProgressionManager() const { return ProgressionManager; }

	UFUNCTION(BlueprintPure, Category = "Game")
	ACSVCardShow* GetCurrentShow() const { return CurrentShow; }

	// Game flow
	UFUNCTION(BlueprintCallable, Category = "Game")
	bool StartCardShow(int32 ShowTier);

	UFUNCTION(BlueprintCallable, Category = "Game")
	void EndCardShow();

	UFUNCTION(BlueprintCallable, Category = "Game")
	void PauseGame();

	UFUNCTION(BlueprintCallable, Category = "Game")
	void ResumeGame();

	// Time management
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Game|Time")
	float GameTimeScale = 60.0f; // 1 real second = 1 game minute

	UPROPERTY(BlueprintReadOnly, Category = "Game|Time")
	float CurrentGameTime = 0.0f;

	UFUNCTION(BlueprintPure, Category = "Game|Time")
	int32 GetGameHour() const;

	UFUNCTION(BlueprintPure, Category = "Game|Time")
	int32 GetGameDay() const;

protected:
	UPROPERTY()
	UCSVCardDatabase* CardDatabase;

	UPROPERTY()
	UCSVEconomyManager* EconomyManager;

	UPROPERTY()
	UCSVProgressionManager* ProgressionManager;

	UPROPERTY()
	ACSVCardShow* CurrentShow;

	UPROPERTY()
	bool bGamePaused;

	UPROPERTY(EditDefaultsOnly, Category = "Game")
	TSubclassOf<ACSVCardShow> CardShowClass;

private:
	void InitializeSubsystems();
	void UpdateGameTime(float DeltaSeconds);
};
