#pragma once

#include <memory>

#include "../Common_App/DhtClient/ConnectionPool.h"
#include "DhtClientApp.h"

namespace Decent
{
	namespace DhtClient
	{
		struct DhtClientAppPkg
		{
			std::shared_ptr<ConnectionPool> m_cntPool;
			std::unique_ptr<DhtClientApp> m_app;
		};
	}
}
