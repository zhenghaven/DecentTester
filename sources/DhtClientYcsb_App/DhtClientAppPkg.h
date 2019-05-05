#pragma once

#include <memory>

#include "DhtClientApp.h"
#include "DhtClient/ConnectionPool.h"

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
