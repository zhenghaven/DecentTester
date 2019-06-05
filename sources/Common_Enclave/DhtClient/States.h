#pragma once

#include <vector>

#include <DecentApi/Common/general_key_types.h>
#include <DecentApi/Common/Ra/TlsConfigWithName.h>
#include <DecentApi/Common/Tools/SharedCachingQueue.h>

#include <DecentApi/DecentAppEnclave/AppStates.h>

#include "AccessCtrl/FullPolicy.h"

namespace Decent
{
	namespace DhtClient
	{
		class ConnectionManager;

		class States : public Ra::AppStates
		{
		public:
			States(Ra::AppCertContainer & certCntnr, Ra::KeyContainer & keyCntnr, Ra::WhiteList::DecentServer & serverWl, GetLoadedWlFunc getLoadedFunc, ConnectionManager& cntMgr) :
				AppStates(certCntnr, keyCntnr, serverWl, getLoadedFunc),
				m_cntMgr(cntMgr),
				m_attrCache(10)
			{}

			virtual ~States()
			{}

			const ConnectionManager& GetConnectionMgr() const
			{
				return m_cntMgr;
			}

			ConnectionManager& GetConnectionMgr()
			{
				return m_cntMgr;
			}

			const Tools::SharedCachingQueue<uint64_t, std::vector<uint8_t> >& GetAttributeCache() const
			{
				return m_attrCache;
			}

			Tools::SharedCachingQueue<uint64_t, std::vector<uint8_t> >& GetAttributeCache()
			{
				return m_attrCache;
			}

			std::shared_ptr<Dht::AccessCtrl::FullPolicy>& GetTestAccPolicy()
			{
				return m_testAccPolicy;
			}

			const std::shared_ptr<Dht::AccessCtrl::FullPolicy>& GetTestAccPolicy() const
			{
				return m_testAccPolicy;
			}

			void SetTlsConfigToDht(std::shared_ptr<Ra::TlsConfigWithName> tlsCfg2Dht)
			{
				m_tlsCfg2Dht = tlsCfg2Dht;
			}

			std::shared_ptr<Ra::TlsConfigWithName> GetTlsConfigToDht() const
			{
				return m_tlsCfg2Dht;
			}

		private:
			ConnectionManager& m_cntMgr;

			Tools::SharedCachingQueue<uint64_t, std::vector<uint8_t> > m_attrCache;

			std::shared_ptr<Dht::AccessCtrl::FullPolicy> m_testAccPolicy;

			std::shared_ptr<Ra::TlsConfigWithName> m_tlsCfg2Dht;
		};
	}
}
