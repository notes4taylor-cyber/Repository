// Copyright Card Show Vendor. All Rights Reserved.

#include "Core/CSVGameMode.h"
#include "Core/CSVPlayerController.h"
#include "Core/CSVPlayerState.h"
#include "Cards/CSVCardDatabase.h"
#include "Economy/CSVEconomyManager.h"
#include "Economy/CSVProgressionManager.h"
#include "Shows/CSVCardShow.h"
#include "CardShowVendor.h"

ACSVGameMode::ACSVGameMode()
{
	PrimaryActorTick.bCanEverTick = true;

	PlayerControllerClass = ACSVPlayerController::StaticClass();
	PlayerStateClass = ACSVPlayerState::StaticClass();

	CardDatabase = nullptr;
	EconomyManager = nullptr;
	ProgressionManager = nullptr;
	CurrentShow = nullptr;
	bGamePaused = false;
}

void ACSVGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
	Super::InitGame(MapName, Options, ErrorMessage);
	InitializeSubsystems();
}

void ACSVGameMode::StartPlay()
{
	Super::StartPlay();
	UE_LOG(LogCardShowVendor, Log, TEXT("Card Show Vendor game started!"));
}

void ACSVGameMode::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!bGamePaused)
	{
		UpdateGameTime(DeltaSeconds);

		if (EconomyManager)
		{
			EconomyManager->TickEconomy(DeltaSeconds);
		}

		if (ProgressionManager)
		{
			ProgressionManager->UpdatePlayTime(DeltaSeconds / 3600.0f);
		}
	}
}

void ACSVGameMode::InitializeSubsystems()
{
	// Create card database
	CardDatabase = NewObject<UCSVCardDatabase>(this);
	CardDatabase->InitializeDatabase();

	// Create economy manager
	EconomyManager = NewObject<UCSVEconomyManager>(this);
	EconomyManager->Initialize();

	// Create progression manager
	ProgressionManager = NewObject<UCSVProgressionManager>(this);
	ProgressionManager->Initialize();

	UE_LOG(LogCardShowVendor, Log, TEXT("Game subsystems initialized"));
}

bool ACSVGameMode::StartCardShow(int32 ShowTier)
{
	if (CurrentShow)
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Cannot start show - already in a show"));
		return false;
	}

	if (ProgressionManager && !ProgressionManager->CanAccessTier(ShowTier))
	{
		UE_LOG(LogCardShowVendor, Warning, TEXT("Cannot access show tier %d"), ShowTier);
		return false;
	}

	// Spawn the card show
	TSubclassOf<ACSVCardShow> ClassToSpawn = CardShowClass ? CardShowClass : ACSVCardShow::StaticClass();
	
	FActorSpawnParameters SpawnParams;
	CurrentShow = GetWorld()->SpawnActor<ACSVCardShow>(ClassToSpawn, FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

	if (CurrentShow)
	{
		CurrentShow->InitializeShow(ShowTier);

		if (ProgressionManager)
		{
			ProgressionManager->RecordShowAttended();
		}

		UE_LOG(LogCardShowVendor, Log, TEXT("Card show started at tier %d"), ShowTier);
		return true;
	}

	return false;
}

void ACSVGameMode::EndCardShow()
{
	if (!CurrentShow)
	{
		return;
	}

	// Calculate and award reputation
	if (ProgressionManager)
	{
		int32 RepGain = CurrentShow->CalculateReputationGain();
		ProgressionManager->AddReputation(RepGain);
	}

	CurrentShow->FinalizeShow();
	CurrentShow->Destroy();
	CurrentShow = nullptr;

	UE_LOG(LogCardShowVendor, Log, TEXT("Card show ended"));
}

void ACSVGameMode::PauseGame()
{
	bGamePaused = true;
}

void ACSVGameMode::ResumeGame()
{
	bGamePaused = false;
}

void ACSVGameMode::UpdateGameTime(float DeltaSeconds)
{
	CurrentGameTime += DeltaSeconds * GameTimeScale;
}

int32 ACSVGameMode::GetGameHour() const
{
	return FMath::FloorToInt(FMath::Fmod(CurrentGameTime / 60.0f, 24.0f));
}

int32 ACSVGameMode::GetGameDay() const
{
	return FMath::FloorToInt(CurrentGameTime / (60.0f * 24.0f)) + 1;
}
