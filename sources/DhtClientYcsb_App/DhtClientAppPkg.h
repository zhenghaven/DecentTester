#pragma once

#include <memory>

#include "DhtClientApp.h"

namespace Decent
{
	namespace DhtClient
	{
		class ConnectionPool;

		struct DhtClientAppPkg
		{
			std::shared_ptr<ConnectionPool> m_cntPool;
			std::unique_ptr<DhtClientApp> m_app;
		};
	}
}
