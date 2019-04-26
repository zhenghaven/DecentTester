#include "EnclaveInitializer.h"

#include <boost/filesystem.hpp>

#include <DecentApi/Common/Ra/WhiteList/WhiteList.h>

#include <DecentApi/CommonApp/Ra/Messages.h>
#include <DecentApi/CommonApp/Tools/DiskFile.h>
#include <DecentApi/CommonApp/Tools/ConfigManager.h>
#include <DecentApi/CommonApp/Net/TCPConnection.h>

#include "ConnectionManager.h"
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
		DiskFile file(gsk_configFilePaht, FileBase::Mode::Read);

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

	const ConfigItem& GetDecentServerItem()
	{
		static const ConfigItem& decentServerItem = GetConfigManager().GetItem(WhiteList::sk_nameDecentServer);
		return decentServerItem;
	}

	std::unique_ptr<Connection> GetDecentServerConnection()
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
		ConnectionManager::SetConfigManager(GetConfigManager());
		GetDecentServerConnection()->SendPack(Message::LoadWhiteList(gsk_whiteListKey, GetConfigManager().GetLoadedWhiteListStr()));
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

JNIEXPORT DhtClientApp* JNICALL DhtClient::GetNewDhtClientApp()
{
	return new DhtClientApp(ENCLAVE_FILENAME, KnownFolderType::LocalAppDataEnclave, TOKEN_FILENAME, gsk_whiteListKey, *GetDecentServerConnection());
}
