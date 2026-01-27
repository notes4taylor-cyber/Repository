// Copyright Card Show Vendor. All Rights Reserved.

#include "Cards/CSVCardDatabase.h"
#include "Cards/CSVCardData.h"
#include "Cards/CSVCardInstance.h"
#include "CardShowVendor.h"

UCSVCardDatabase::UCSVCardDatabase()
{
}

void UCSVCardDatabase::InitializeDatabase()
{
	// Generate default cards if none registered
	if (RegisteredCards.Num() == 0)
	{
		GenerateDefaultCards();
	}

	// Setup default pack configurations
	if (AvailablePacks.Num() == 0)
	{
		// Baseball Base Pack
		FCSVPackConfiguration BaseballPack;
		BaseballPack.PackName = TEXT("BaseballBase");
		BaseballPack.CardsPerPack = 10;
		BaseballPack.PackPrice = 5.0f;
		BaseballPack.GuaranteedRares = 0;
		BaseballPack.Sport = ECSVCardSport::Baseball;
		BaseballPack.RarityWeights.Add(ECSVCardRarity::Common, 60.0f);
		BaseballPack.RarityWeights.Add(ECSVCardRarity::Uncommon, 25.0f);
		BaseballPack.RarityWeights.Add(ECSVCardRarity::Rare, 10.0f);
		BaseballPack.RarityWeights.Add(ECSVCardRarity::UltraRare, 4.0f);
		BaseballPack.RarityWeights.Add(ECSVCardRarity::Legendary, 1.0f);
		AvailablePacks.Add(BaseballPack);

		// Basketball Premium Pack
		FCSVPackConfiguration BasketballPack;
		BasketballPack.PackName = TEXT("BasketballPremium");
		BasketballPack.CardsPerPack = 8;
		BasketballPack.PackPrice = 15.0f;
		BasketballPack.GuaranteedRares = 1;
		BasketballPack.Sport = ECSVCardSport::Basketball;
		BasketballPack.RarityWeights.Add(ECSVCardRarity::Common, 40.0f);
		BasketballPack.RarityWeights.Add(ECSVCardRarity::Uncommon, 30.0f);
		BasketballPack.RarityWeights.Add(ECSVCardRarity::Rare, 18.0f);
		BasketballPack.RarityWeights.Add(ECSVCardRarity::UltraRare, 9.0f);
		BasketballPack.RarityWeights.Add(ECSVCardRarity::Legendary, 3.0f);
		AvailablePacks.Add(BasketballPack);

		// Pokemon Pack
		FCSVPackConfiguration PokemonPack;
		PokemonPack.PackName = TEXT("PokemonBooster");
		PokemonPack.CardsPerPack = 11;
		PokemonPack.PackPrice = 4.0f;
		PokemonPack.GuaranteedRares = 1;
		PokemonPack.Sport = ECSVCardSport::Pokemon;
		PokemonPack.RarityWeights.Add(ECSVCardRarity::Common, 55.0f);
		PokemonPack.RarityWeights.Add(ECSVCardRarity::Uncommon, 28.0f);
		PokemonPack.RarityWeights.Add(ECSVCardRarity::Rare, 12.0f);
		PokemonPack.RarityWeights.Add(ECSVCardRarity::UltraRare, 4.0f);
		PokemonPack.RarityWeights.Add(ECSVCardRarity::Legendary, 1.0f);
		AvailablePacks.Add(PokemonPack);
	}

	BuildCaches();

	UE_LOG(LogCardShowVendor, Log, TEXT("Card Database initialized with %d cards and %d pack types"),
		RegisteredCards.Num(), AvailablePacks.Num());
}

void UCSVCardDatabase::GenerateDefaultCards()
{
	// Baseball Legends
	CreateRuntimeCardData(TEXT("BB_RUTH_1933"), TEXT("Babe Ruth"), TEXT("Yankees"), 1933, TEXT("Goudey"), ECSVCardSport::Baseball, ECSVCardRarity::Legendary, 500.0f, 53);
	CreateRuntimeCardData(TEXT("BB_MANTLE_1952"), TEXT("Mickey Mantle"), TEXT("Yankees"), 1952, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::Legendary, 750.0f, 311);
	CreateRuntimeCardData(TEXT("BB_AARON_1954"), TEXT("Hank Aaron"), TEXT("Braves"), 1954, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::UltraRare, 200.0f, 128);
	CreateRuntimeCardData(TEXT("BB_TROUT_2011"), TEXT("Mike Trout"), TEXT("Angels"), 2011, TEXT("Topps Update"), ECSVCardSport::Baseball, ECSVCardRarity::UltraRare, 150.0f, 175);
	CreateRuntimeCardData(TEXT("BB_OHTANI_2018"), TEXT("Shohei Ohtani"), TEXT("Angels"), 2018, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::Rare, 50.0f, 700);
	CreateRuntimeCardData(TEXT("BB_JUDGE_2017"), TEXT("Aaron Judge"), TEXT("Yankees"), 2017, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::Rare, 40.0f, 287);

	// Baseball Commons/Uncommons
	CreateRuntimeCardData(TEXT("BB_SMITH_2023"), TEXT("Will Smith"), TEXT("Dodgers"), 2023, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::Uncommon, 2.0f, 45);
	CreateRuntimeCardData(TEXT("BB_GARCIA_2023"), TEXT("Adolis Garcia"), TEXT("Rangers"), 2023, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::Uncommon, 3.0f, 112);
	CreateRuntimeCardData(TEXT("BB_ROOKIE1_2024"), TEXT("Jackson Holliday"), TEXT("Orioles"), 2024, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::Common, 1.0f, 250);
	CreateRuntimeCardData(TEXT("BB_COMMON1_2024"), TEXT("Marcus Semien"), TEXT("Rangers"), 2024, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::Common, 0.5f, 88);
	CreateRuntimeCardData(TEXT("BB_COMMON2_2024"), TEXT("Mookie Betts"), TEXT("Dodgers"), 2024, TEXT("Topps"), ECSVCardSport::Baseball, ECSVCardRarity::Common, 1.0f, 50);

	// Basketball Legends
	CreateRuntimeCardData(TEXT("BK_JORDAN_1986"), TEXT("Michael Jordan"), TEXT("Bulls"), 1986, TEXT("Fleer"), ECSVCardSport::Basketball, ECSVCardRarity::Legendary, 1000.0f, 57);
	CreateRuntimeCardData(TEXT("BK_LEBRON_2003"), TEXT("LeBron James"), TEXT("Cavaliers"), 2003, TEXT("Topps Chrome"), ECSVCardSport::Basketball, ECSVCardRarity::Legendary, 600.0f, 111);
	CreateRuntimeCardData(TEXT("BK_KOBE_1996"), TEXT("Kobe Bryant"), TEXT("Lakers"), 1996, TEXT("Topps Chrome"), ECSVCardSport::Basketball, ECSVCardRarity::UltraRare, 300.0f, 138);
	CreateRuntimeCardData(TEXT("BK_CURRY_2009"), TEXT("Stephen Curry"), TEXT("Warriors"), 2009, TEXT("Topps"), ECSVCardSport::Basketball, ECSVCardRarity::UltraRare, 200.0f, 321);
	CreateRuntimeCardData(TEXT("BK_WEMBY_2023"), TEXT("Victor Wembanyama"), TEXT("Spurs"), 2023, TEXT("Prizm"), ECSVCardSport::Basketball, ECSVCardRarity::Rare, 75.0f, 1);

	// Basketball Commons/Uncommons
	CreateRuntimeCardData(TEXT("BK_TATUM_2024"), TEXT("Jayson Tatum"), TEXT("Celtics"), 2024, TEXT("Prizm"), ECSVCardSport::Basketball, ECSVCardRarity::Uncommon, 5.0f, 22);
	CreateRuntimeCardData(TEXT("BK_COMMON1_2024"), TEXT("Tyrese Haliburton"), TEXT("Pacers"), 2024, TEXT("Prizm"), ECSVCardSport::Basketball, ECSVCardRarity::Common, 1.5f, 45);
	CreateRuntimeCardData(TEXT("BK_COMMON2_2024"), TEXT("Anthony Edwards"), TEXT("Timberwolves"), 2024, TEXT("Prizm"), ECSVCardSport::Basketball, ECSVCardRarity::Common, 2.0f, 78);

	// Football
	CreateRuntimeCardData(TEXT("FB_BRADY_2000"), TEXT("Tom Brady"), TEXT("Patriots"), 2000, TEXT("Bowman Chrome"), ECSVCardSport::Football, ECSVCardRarity::Legendary, 800.0f, 236);
	CreateRuntimeCardData(TEXT("FB_MAHOMES_2017"), TEXT("Patrick Mahomes"), TEXT("Chiefs"), 2017, TEXT("Prizm"), ECSVCardSport::Football, ECSVCardRarity::UltraRare, 250.0f, 269);
	CreateRuntimeCardData(TEXT("FB_STROUD_2023"), TEXT("C.J. Stroud"), TEXT("Texans"), 2023, TEXT("Prizm"), ECSVCardSport::Football, ECSVCardRarity::Rare, 35.0f, 301);
	CreateRuntimeCardData(TEXT("FB_COMMON1_2024"), TEXT("Jalen Hurts"), TEXT("Eagles"), 2024, TEXT("Prizm"), ECSVCardSport::Football, ECSVCardRarity::Uncommon, 4.0f, 215);
	CreateRuntimeCardData(TEXT("FB_COMMON2_2024"), TEXT("Travis Kelce"), TEXT("Chiefs"), 2024, TEXT("Prizm"), ECSVCardSport::Football, ECSVCardRarity::Common, 2.0f, 87);

	// Pokemon
	CreateRuntimeCardData(TEXT("PKM_CHARIZARD_1999"), TEXT("Charizard"), TEXT("Base Set"), 1999, TEXT("Base Set"), ECSVCardSport::Pokemon, ECSVCardRarity::Legendary, 500.0f, 4);
	CreateRuntimeCardData(TEXT("PKM_PIKACHU_1999"), TEXT("Pikachu"), TEXT("Base Set"), 1999, TEXT("Base Set"), ECSVCardSport::Pokemon, ECSVCardRarity::UltraRare, 100.0f, 58);
	CreateRuntimeCardData(TEXT("PKM_MEWTWO_1999"), TEXT("Mewtwo"), TEXT("Base Set"), 1999, TEXT("Base Set"), ECSVCardSport::Pokemon, ECSVCardRarity::Rare, 50.0f, 10);
	CreateRuntimeCardData(TEXT("PKM_BLASTOISE_1999"), TEXT("Blastoise"), TEXT("Base Set"), 1999, TEXT("Base Set"), ECSVCardSport::Pokemon, ECSVCardRarity::Rare, 75.0f, 2);
	CreateRuntimeCardData(TEXT("PKM_COMMON1_2024"), TEXT("Pikachu EX"), TEXT("151"), 2024, TEXT("Scarlet & Violet 151"), ECSVCardSport::Pokemon, ECSVCardRarity::Uncommon, 8.0f, 163);
	CreateRuntimeCardData(TEXT("PKM_COMMON2_2024"), TEXT("Bulbasaur"), TEXT("151"), 2024, TEXT("Scarlet & Violet 151"), ECSVCardSport::Pokemon, ECSVCardRarity::Common, 0.5f, 1);
	CreateRuntimeCardData(TEXT("PKM_COMMON3_2024"), TEXT("Squirtle"), TEXT("151"), 2024, TEXT("Scarlet & Violet 151"), ECSVCardSport::Pokemon, ECSVCardRarity::Common, 0.5f, 7);

	// Magic: The Gathering
	CreateRuntimeCardData(TEXT("MTG_LOTUS_1993"), TEXT("Black Lotus"), TEXT("Alpha"), 1993, TEXT("Alpha"), ECSVCardSport::MagicTheGathering, ECSVCardRarity::Legendary, 5000.0f, 1);
	CreateRuntimeCardData(TEXT("MTG_MOX_1993"), TEXT("Mox Ruby"), TEXT("Alpha"), 1993, TEXT("Alpha"), ECSVCardSport::MagicTheGathering, ECSVCardRarity::UltraRare, 1000.0f, 2);
	CreateRuntimeCardData(TEXT("MTG_JACE_2011"), TEXT("Jace, the Mind Sculptor"), TEXT("Worldwake"), 2011, TEXT("Worldwake"), ECSVCardSport::MagicTheGathering, ECSVCardRarity::Rare, 50.0f, 31);
	CreateRuntimeCardData(TEXT("MTG_COMMON1_2024"), TEXT("Lightning Bolt"), TEXT("Foundations"), 2024, TEXT("Foundations"), ECSVCardSport::MagicTheGathering, ECSVCardRarity::Uncommon, 2.0f, 145);
	CreateRuntimeCardData(TEXT("MTG_COMMON2_2024"), TEXT("Forest"), TEXT("Foundations"), 2024, TEXT("Foundations"), ECSVCardSport::MagicTheGathering, ECSVCardRarity::Common, 0.1f, 270);

	UE_LOG(LogCardShowVendor, Log, TEXT("Generated %d default cards"), RegisteredCards.Num());
}

UCSVCardData* UCSVCardDatabase::CreateRuntimeCardData(
	FName ID,
	const FString& PlayerName,
	const FString& Team,
	int32 Year,
	const FString& SetName,
	ECSVCardSport Sport,
	ECSVCardRarity Rarity,
	float BaseValue,
	int32 CardNumber)
{
	UCSVCardData* CardData = NewObject<UCSVCardData>(this, UCSVCardData::StaticClass(), ID);

	CardData->CardID = ID;
	CardData->PlayerName = FText::FromString(PlayerName);
	CardData->TeamName = FText::FromString(Team);
	CardData->Year = Year;
	CardData->SetName = FText::FromString(SetName);
	CardData->CardName = FText::FromString(FString::Printf(TEXT("%d %s %s"), Year, *SetName, *PlayerName));
	CardData->CardNumber = FText::FromString(FString::Printf(TEXT("#%d"), CardNumber));
	CardData->Sport = Sport;
	CardData->Rarity = Rarity;
	CardData->BaseValue = BaseValue;

	// Set era based on year
	if (Year < 1980)
	{
		CardData->Era = ECSVCardEra::Vintage;
	}
	else if (Year < 1995)
	{
		CardData->Era = ECSVCardEra::JunkWax;
	}
	else if (Year < 2010)
	{
		CardData->Era = ECSVCardEra::Modern;
	}
	else
	{
		CardData->Era = ECSVCardEra::Ultra_Modern;
	}

	// Spawn weight based on rarity
	switch (Rarity)
	{
	case ECSVCardRarity::Common:		CardData->SpawnWeight = 100.0f; break;
	case ECSVCardRarity::Uncommon:		CardData->SpawnWeight = 40.0f; break;
	case ECSVCardRarity::Rare:			CardData->SpawnWeight = 10.0f; break;
	case ECSVCardRarity::UltraRare:		CardData->SpawnWeight = 2.0f; break;
	case ECSVCardRarity::Legendary:		CardData->SpawnWeight = 0.5f; break;
	case ECSVCardRarity::OneOfOne:		CardData->SpawnWeight = 0.01f; break;
	}

	RegisteredCards.Add(CardData);
	return CardData;
}

void UCSVCardDatabase::BuildCaches()
{
	CardsBySport.Empty();
	CardsByRarity.Empty();

	for (UCSVCardData* Card : RegisteredCards)
	{
		if (!Card) continue;

		// Cache by sport
		if (!CardsBySport.Contains(Card->Sport))
		{
			CardsBySport.Add(Card->Sport, TArray<UCSVCardData*>());
		}
		CardsBySport[Card->Sport].Add(Card);

		// Cache by rarity
		if (!CardsByRarity.Contains(Card->Rarity))
		{
			CardsByRarity.Add(Card->Rarity, TArray<UCSVCardData*>());
		}
		CardsByRarity[Card->Rarity].Add(Card);
	}
}

TArray<UCSVCardData*> UCSVCardDatabase::GetCardsBySport(ECSVCardSport Sport) const
{
	if (CardsBySport.Contains(Sport))
	{
		return CardsBySport[Sport];
	}
	return TArray<UCSVCardData*>();
}

TArray<UCSVCardData*> UCSVCardDatabase::GetCardsByRarity(ECSVCardRarity Rarity) const
{
	if (CardsByRarity.Contains(Rarity))
	{
		return CardsByRarity[Rarity];
	}
	return TArray<UCSVCardData*>();
}

TArray<UCSVCardData*> UCSVCardDatabase::GetCardsByEra(ECSVCardEra Era) const
{
	TArray<UCSVCardData*> Result;
	for (UCSVCardData* Card : RegisteredCards)
	{
		if (Card && Card->Era == Era)
		{
			Result.Add(Card);
		}
	}
	return Result;
}

UCSVCardData* UCSVCardDatabase::GetCardByID(FName CardID) const
{
	for (UCSVCardData* Card : RegisteredCards)
	{
		if (Card && Card->CardID == CardID)
		{
			return Card;
		}
	}
	return nullptr;
}

UCSVCardData* UCSVCardDatabase::GetRandomCard(ECSVCardSport Sport) const
{
	TArray<UCSVCardData*> SportCards = GetCardsBySport(Sport);
	if (SportCards.Num() == 0)
	{
		if (RegisteredCards.Num() > 0)
		{
			return RegisteredCards[FMath::RandRange(0, RegisteredCards.Num() - 1)];
		}
		return nullptr;
	}

	// Weighted random selection
	float TotalWeight = 0.0f;
	for (UCSVCardData* Card : SportCards)
	{
		TotalWeight += Card->SpawnWeight;
	}

	float Roll = FMath::FRandRange(0.0f, TotalWeight);
	float CurrentWeight = 0.0f;

	for (UCSVCardData* Card : SportCards)
	{
		CurrentWeight += Card->SpawnWeight;
		if (Roll <= CurrentWeight)
		{
			return Card;
		}
	}

	return SportCards.Last();
}

UCSVCardData* UCSVCardDatabase::GetRandomCardByRarity(ECSVCardRarity Rarity) const
{
	TArray<UCSVCardData*> RarityCards = GetCardsByRarity(Rarity);
	if (RarityCards.Num() == 0)
	{
		return nullptr;
	}
	return RarityCards[FMath::RandRange(0, RarityCards.Num() - 1)];
}

UCSVCardInstance* UCSVCardDatabase::GenerateCardInstance(UCSVCardData* CardData, UObject* Outer)
{
	if (!CardData)
	{
		return nullptr;
	}

	UCSVCardInstance* Instance = NewObject<UCSVCardInstance>(Outer ? Outer : this);
	Instance->InitializeFromData(CardData);
	return Instance;
}

UCSVCardInstance* UCSVCardDatabase::GenerateRandomCardInstance(ECSVCardSport Sport, UObject* Outer)
{
	UCSVCardData* CardData = GetRandomCard(Sport);
	return GenerateCardInstance(CardData, Outer);
}

ECSVCardRarity UCSVCardDatabase::RollRarity(const TMap<ECSVCardRarity, float>& Weights) const
{
	float TotalWeight = 0.0f;
	for (const auto& Pair : Weights)
	{
		TotalWeight += Pair.Value;
	}

	float Roll = FMath::FRandRange(0.0f, TotalWeight);
	float CurrentWeight = 0.0f;

	for (const auto& Pair : Weights)
	{
		CurrentWeight += Pair.Value;
		if (Roll <= CurrentWeight)
		{
			return Pair.Key;
		}
	}

	return ECSVCardRarity::Common;
}

TArray<UCSVCardInstance*> UCSVCardDatabase::OpenPack(const FCSVPackConfiguration& PackConfig, UObject* Outer)
{
	TArray<UCSVCardInstance*> PackContents;

	// Handle guaranteed rares first
	for (int32 i = 0; i < PackConfig.GuaranteedRares; ++i)
	{
		UCSVCardData* RareCard = nullptr;
		TArray<UCSVCardData*> SportCards = GetCardsBySport(PackConfig.Sport);

		// Find a rare or better card
		TArray<UCSVCardData*> RareOrBetter;
		for (UCSVCardData* Card : SportCards)
		{
			if (Card && Card->Rarity >= ECSVCardRarity::Rare)
			{
				RareOrBetter.Add(Card);
			}
		}

		if (RareOrBetter.Num() > 0)
		{
			RareCard = RareOrBetter[FMath::RandRange(0, RareOrBetter.Num() - 1)];
			UCSVCardInstance* Instance = GenerateCardInstance(RareCard, Outer);
			if (Instance)
			{
				PackContents.Add(Instance);
			}
		}
	}

	// Fill remaining slots with weighted random
	int32 RemainingSlots = PackConfig.CardsPerPack - PackContents.Num();
	for (int32 i = 0; i < RemainingSlots; ++i)
	{
		ECSVCardRarity Rarity = RollRarity(PackConfig.RarityWeights);
		TArray<UCSVCardData*> SportCards = GetCardsBySport(PackConfig.Sport);

		// Find cards of this rarity for this sport
		TArray<UCSVCardData*> MatchingCards;
		for (UCSVCardData* Card : SportCards)
		{
			if (Card && Card->Rarity == Rarity)
			{
				MatchingCards.Add(Card);
			}
		}

		// Fallback to any card of this sport if no matching rarity
		if (MatchingCards.Num() == 0)
		{
			MatchingCards = SportCards;
		}

		if (MatchingCards.Num() > 0)
		{
			UCSVCardData* CardData = MatchingCards[FMath::RandRange(0, MatchingCards.Num() - 1)];
			UCSVCardInstance* Instance = GenerateCardInstance(CardData, Outer);
			if (Instance)
			{
				PackContents.Add(Instance);
			}
		}
	}

	UE_LOG(LogCardShowVendor, Log, TEXT("Opened pack '%s' - Got %d cards"),
		*PackConfig.PackName.ToString(), PackContents.Num());

	return PackContents;
}

FCSVPackConfiguration UCSVCardDatabase::GetPackByName(FName PackName) const
{
	for (const FCSVPackConfiguration& Pack : AvailablePacks)
	{
		if (Pack.PackName == PackName)
		{
			return Pack;
		}
	}
	return FCSVPackConfiguration();
}

int32 UCSVCardDatabase::GetCardCountBySport(ECSVCardSport Sport) const
{
	if (CardsBySport.Contains(Sport))
	{
		return CardsBySport[Sport].Num();
	}
	return 0;
}
