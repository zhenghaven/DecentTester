#include "EnclaveInitializer.h"

#include <boost/filesystem.hpp>

#include <DecentApi/Common/make_unique.h>
#include <DecentApi/Common/Ra/RequestCategory.h>
#include <DecentApi/Common/Ra/WhiteList/WhiteList.h>

#include <DecentApi/CommonApp/Net/TCPConnection.h>
#include <DecentApi/CommonApp/Tools/DiskFile.h>
#include <DecentApi/CommonApp/Tools/FileSystemUtil.h>

#include <DecentApi/DecentAppApp/DecentAppConfig.h>

#include "../Common_App/DhtClient/ConnectionPool.h"
#include "DhtClientApp.h"
#include "DhtClientAppPkg.h"

using namespace Decent;
using namespace Decent::Ra;
using namespace Decent::Net;
using namespace Decent::Tools;
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

	const AppConfig::DecentAppConfig& GetConfigManager()
	{
		static AppConfig::DecentAppConfig configManager(GetConfigJsonStr());

		return configManager;
	}

	const AppConfig::EnclaveListItem& GetDecentServerItem()
	{
		static const AppConfig::EnclaveListItem& decentServerItem =
			GetConfigManager().GetEnclaveList().GetItem(WhiteList::sk_nameDecentServer);
		return decentServerItem;
	}

	std::unique_ptr<ConnectionBase> GetDecentServerConnection()
	{
		static uint32_t serverIp = TCPConnection::GetIpAddressFromStr(GetDecentServerItem().GetAddr());
		return std::make_unique<TCPConnection>(serverIp, GetDecentServerItem().GetPort());
	}

	class Initializer
	{
	public:
		Initializer();
		~Initializer();

	private:

	};

	Initializer::Initializer()
	{
		std::unique_ptr<ConnectionBase> serverCon = GetDecentServerConnection();
		serverCon->SendContainer(Ra::RequestCategory::sk_loadWhiteList);
		serverCon->SendContainer(gsk_whiteListKey);
		serverCon->SendContainer(GetConfigManager().GetEnclaveList().GetLoadedWhiteListStr());
		char ackMsg[] = "ACK";
		serverCon->RecvRawAll(&ackMsg, sizeof(ackMsg));
	}

	Initializer::~Initializer()
	{
	}
}

JNIEXPORT void* JNICALL DhtClient::Initialize()
{
	static Initializer inst;
	return &inst;
}

JNIEXPORT DhtClientAppPkg* JNICALL DhtClient::GetNewDhtClientAppPkg(size_t cntPoolSize, int64_t maxOpPerTicket)
{
	DhtClient::Initialize();
	boost::filesystem::path tokenPath = GetKnownFolderPath(KnownFolderType::LocalAppDataEnclave).append(TOKEN_FILENAME);

	DhtClientAppPkg* res = new DhtClientAppPkg;
	res->m_cntPool = std::make_shared<ConnectionPool>(0, cntPoolSize, GetConfigManager().GetEnclaveList());
	res->m_app = Tools::make_unique<DhtClientApp>(ENCLAVE_FILENAME, tokenPath, gsk_whiteListKey, *GetDecentServerConnection());

	res->m_app->Init(maxOpPerTicket, res->m_cntPool->GetKnownNodeAddr());

	return res;
}
