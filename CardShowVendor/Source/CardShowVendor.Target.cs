// Copyright Card Show Vendor. All Rights Reserved.

using UnrealBuildTool;
using System.Collections.Generic;

public class CardShowVendorTarget : TargetRules
{
	public CardShowVendorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V4;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_3;
		ExtraModuleNames.Add("CardShowVendor");
	}
}
