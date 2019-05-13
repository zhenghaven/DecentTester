#include "EnclaveInitializer.h"

#include <boost/filesystem.hpp>

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/Ra/RequestCategory.h>
#include <DecentApi/Common/Ra/WhiteList/WhiteList.h>

#include <DecentApi/CommonApp/Tools/DiskFile.h>
#include <DecentApi/CommonApp/Tools/ConfigManager.h>

#include "DhtClientAppPkg.h"
#include "../Common_App/DhtClient/ConnectionPool.h"
#include "DhtClientApp.h"

using namespace Decent;
using namespace Decent::Tools;
using namespace Decent::Ra;
using namespace Decent::Net;
using namespace Decent::DhtClient;

namespace
{
	constexpr char gsk_configFilePaht[] = "Config.json";
	constexpr char gsk_whiteListKey[] = "DhtTestClientWhiteList";

	std::string GetConfigJsonStr()
	{
		DiskFile file(gsk_configFilePaht, FileBase::Mode::Read, false);

		std::string res;
		res.resize(file.GetFileSize());
		file.ReadBlockExactSize(res);

		return res;
	}

	const ConfigManager& GetConfigManager()
	{
		static ConfigManager configManager(GetConfigJsonStr());

		return configManager;
	}
}

JNIEXPORT DhtClientAppPkg* JNICALL DhtClient::GetNewDhtClientAppPkg(size_t cntPoolSize)
{
	DhtClientAppPkg* res = new DhtClientAppPkg;
	res->m_cntPool = std::make_shared<ConnectionPool>(0, cntPoolSize, GetConfigManager());
	res->m_app = Tools::make_unique<DhtClientApp>();

	res->m_app->Init();

	return res;
}
