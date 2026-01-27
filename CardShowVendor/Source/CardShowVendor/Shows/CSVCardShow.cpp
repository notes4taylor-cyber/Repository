// Copyright Card Show Vendor. All Rights Reserved.

#include "Shows/CSVCardShow.h"
#include "Booth/CSVVendorBooth.h"
#include "Customers/CSVCustomer.h"
#include "CardShowVendor.h"

ACSVCardShow::ACSVCardShow()
{
	PrimaryActorTick.bCanEverTick = true;

	ShowTier = 0;
	bShowActive = false;
	ShowElapsedTime = 0.0f;
	CustomerSpawnTimer = 0.0f;

	CardsSoldThisShow = 0;
	RevenueThisShow = 0.0f;
	CustomersServedThisShow = 0;
	CustomersLostThisShow = 0;
	HighestSingleSale = 0.0f;

	PlayerBooth = nullptr;

	InitializeShowPresets();
}

void ACSVCardShow::BeginPlay()
{
	Super::BeginPlay();
}

void ACSVCardShow::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bShowActive)
	{
		ShowElapsedTime += DeltaTime;
		UpdateCustomerSpawning(DeltaTime);
	}
}

void ACSVCardShow::InitializeShowPresets()
{
	ShowPresets.Empty();

	// Tier 0: Local Card Show
	FCSVShowConfig Local;
	Local.ShowName = FText::FromString(TEXT("Local Card Show"));
	Local.ShowType = ECSVShowType::LocalShow;
	Local.RequiredTier = 0;
	Local.EntryCost = 25.0f;
	Local.CustomerSpawnRate = 0.8f;
	Local.CustomerWealthMultiplier = 0.8f;
	Local.MaxConcurrentCustomers = 10;
	Local.ShowDurationHours = 6.0f;
	ShowPresets.Add(Local);

	// Tier 1: Community Convention
	FCSVShowConfig Community;
	Community.ShowName = FText::FromString(TEXT("Community Card Convention"));
	Community.ShowType = ECSVShowType::LocalShow;
	Community.RequiredTier = 1;
	Community.EntryCost = 75.0f;
	Community.CustomerSpawnRate = 1.0f;
	Community.CustomerWealthMultiplier = 1.0f;
	Community.MaxConcurrentCustomers = 15;
	Community.ShowDurationHours = 8.0f;
	ShowPresets.Add(Community);

	// Tier 2: Regional Show
	FCSVShowConfig Regional;
	Regional.ShowName = FText::FromString(TEXT("Regional Card Expo"));
	Regional.ShowType = ECSVShowType::RegionalShow;
	Regional.RequiredTier = 2;
	Regional.EntryCost = 150.0f;
	Regional.CustomerSpawnRate = 1.3f;
	Regional.CustomerWealthMultiplier = 1.25f;
	Regional.MaxConcurrentCustomers = 20;
	Regional.ShowDurationHours = 10.0f;
	ShowPresets.Add(Regional);

	// Tier 3: Major Convention
	FCSVShowConfig Major;
	Major.ShowName = FText::FromString(TEXT("Major Sports Card Convention"));
	Major.ShowType = ECSVShowType::NationalShow;
	Major.RequiredTier = 3;
	Major.EntryCost = 350.0f;
	Major.CustomerSpawnRate = 1.6f;
	Major.CustomerWealthMultiplier = 1.5f;
	Major.MaxConcurrentCustomers = 30;
	Major.ShowDurationHours = 12.0f;
	ShowPresets.Add(Major);

	// Tier 4: National Convention
	FCSVShowConfig National;
	National.ShowName = FText::FromString(TEXT("National Sports Collectors Convention"));
	National.ShowType = ECSVShowType::NationalShow;
	National.RequiredTier = 4;
	National.EntryCost = 750.0f;
	National.CustomerSpawnRate = 2.0f;
	National.CustomerWealthMultiplier = 2.0f;
	National.MaxConcurrentCustomers = 40;
	National.ShowDurationHours = 16.0f;
	ShowPresets.Add(National);

	// Tier 5: Premium Showcase
	FCSVShowConfig Premium;
	Premium.ShowName = FText::FromString(TEXT("Elite Collectors Showcase"));
	Premium.ShowType = ECSVShowType::PremiumShow;
	Premium.RequiredTier = 5;
	Premium.EntryCost = 1500.0f;
	Premium.CustomerSpawnRate = 1.5f; // Fewer but wealthier customers
	Premium.CustomerWealthMultiplier = 4.0f;
	Premium.MaxConcurrentCustomers = 25;
	Premium.ShowDurationHours = 8.0f;
	ShowPresets.Add(Premium);
}

FCSVShowConfig ACSVCardShow::GetConfigForTier(int32 Tier) const
{
	if (ShowPresets.IsValidIndex(Tier))
	{
		return ShowPresets[Tier];
	}
	return ShowPresets.IsValidIndex(0) ? ShowPresets[0] : FCSVShowConfig();
}

void ACSVCardShow::InitializeShow(int32 Tier)
{
	ShowTier = Tier;
	ShowConfig = GetConfigForTier(Tier);

	// Reset stats
	CardsSoldThisShow = 0;
	RevenueThisShow = 0.0f;
	CustomersServedThisShow = 0;
	CustomersLostThisShow = 0;
	HighestSingleSale = 0.0f;
	ShowElapsedTime = 0.0f;
	CustomerSpawnTimer = 0.0f;

	bShowActive = true;

	UE_LOG(LogCardShowVendor, Log, TEXT("Show initialized: %s (Tier %d)"),
		*ShowConfig.ShowName.ToString(), ShowTier);
}

void ACSVCardShow::FinalizeShow()
{
	bShowActive = false;

	// Despawn all remaining customers
	for (ACSVCustomer* Customer : ActiveCustomers)
	{
		if (Customer)
		{
			Customer->Destroy();
		}
	}
	ActiveCustomers.Empty();

	UE_LOG(LogCardShowVendor, Log, TEXT("Show finalized: Revenue $%.2f, Sales %d, Customers %d"),
		RevenueThisShow, CardsSoldThisShow, CustomersServedThisShow);
}

void ACSVCardShow::SetPlayerBooth(ACSVVendorBooth* Booth)
{
	PlayerBooth = Booth;
	if (Booth)
	{
		Booth->ResetShowStats();
	}
}

void ACSVCardShow::UpdateCustomerSpawning(float DeltaTime)
{
	CustomerSpawnTimer += DeltaTime;

	// Base spawn interval modified by show's spawn rate
	float SpawnInterval = 10.0f / ShowConfig.CustomerSpawnRate;

	if (CustomerSpawnTimer >= SpawnInterval)
	{
		CustomerSpawnTimer = 0.0f;

		// Check if we can spawn more customers
		if (ActiveCustomers.Num() < ShowConfig.MaxConcurrentCustomers)
		{
			SpawnCustomer();
		}
	}
}

ACSVCustomer* ACSVCardShow::SpawnCustomer()
{
	TSubclassOf<ACSVCustomer> ClassToSpawn = CustomerClass ? CustomerClass : ACSVCustomer::StaticClass();

	// Random spawn position around the show floor
	FVector SpawnLocation = GetActorLocation() + FVector(
		FMath::FRandRange(-500.0f, 500.0f),
		FMath::FRandRange(-500.0f, 500.0f),
		0.0f
	);

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

	ACSVCustomer* NewCustomer = GetWorld()->SpawnActor<ACSVCustomer>(ClassToSpawn, SpawnLocation, FRotator::ZeroRotator, SpawnParams);

	if (NewCustomer)
	{
		// Configure customer based on show settings
		NewCustomer->InitializeCustomer(ShowConfig.CustomerWealthMultiplier);
		NewCustomer->SetTargetBooth(PlayerBooth);

		ActiveCustomers.Add(NewCustomer);

		UE_LOG(LogCardShowVendor, Verbose, TEXT("Customer spawned (Total: %d)"), ActiveCustomers.Num());
	}

	return NewCustomer;
}

void ACSVCardShow::DespawnCustomer(ACSVCustomer* Customer)
{
	if (Customer)
	{
		ActiveCustomers.Remove(Customer);
		Customer->Destroy();
	}
}

void ACSVCardShow::RecordSale(float Amount)
{
	CardsSoldThisShow++;
	RevenueThisShow += Amount;

	if (Amount > HighestSingleSale)
	{
		HighestSingleSale = Amount;
	}

	if (PlayerBooth)
	{
		PlayerBooth->RecordSale(Amount);
	}
}

void ACSVCardShow::RecordCustomerServed(bool bMadePurchase)
{
	CustomersServedThisShow++;
	if (!bMadePurchase)
	{
		CustomersLostThisShow++;
	}
}

int32 ACSVCardShow::CalculateReputationGain() const
{
	int32 BaseRep = 5 * (ShowTier + 1);

	// Bonus for sales
	int32 SalesRep = CardsSoldThisShow * 2;

	// Bonus for revenue milestones
	int32 RevenueRep = FMath::FloorToInt(RevenueThisShow / 100.0f) * 3;

	// Bonus for customer satisfaction (sales vs. served ratio)
	float SatisfactionRate = CustomersServedThisShow > 0 ?
		(float)(CustomersServedThisShow - CustomersLostThisShow) / CustomersServedThisShow : 0.0f;
	int32 SatisfactionRep = FMath::FloorToInt(SatisfactionRate * 20.0f);

	// High value sale bonus
	int32 BigSaleRep = HighestSingleSale >= 100.0f ? 10 : 0;

	int32 TotalRep = BaseRep + SalesRep + RevenueRep + SatisfactionRep + BigSaleRep;

	return FMath::Max(0, TotalRep);
}

float ACSVCardShow::GetShowProgress() const
{
	float TotalSeconds = ShowConfig.ShowDurationHours * 3600.0f;
	return FMath::Clamp(ShowElapsedTime / TotalSeconds, 0.0f, 1.0f);
}

float ACSVCardShow::GetRemainingTime() const
{
	float TotalSeconds = ShowConfig.ShowDurationHours * 3600.0f;
	return FMath::Max(0.0f, TotalSeconds - ShowElapsedTime);
}
