// Copyright Card Show Vendor. All Rights Reserved.

using UnrealBuildTool;

public class CardShowVendor : ModuleRules
{
	public CardShowVendor(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"UMG",
			"Slate",
			"SlateCore",
			"AIModule",
			"NavigationSystem"
		});

		PrivateDependencyModuleNames.AddRange(new string[] {
			"GameplayTasks"
		});
	}
}
