// Copyright Card Show Vendor. All Rights Reserved.

using UnrealBuildTool;
using System.Collections.Generic;

public class CardShowVendorEditorTarget : TargetRules
{
	public CardShowVendorEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V4;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_3;
		ExtraModuleNames.Add("CardShowVendor");
	}
}
