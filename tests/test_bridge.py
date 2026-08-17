"""
QNT 跨链桥接测试
"""
import pytest
from blockchain.bridge import CrossChainBridge, AtomicSwap, create_bridge


class TestCrossChainBridge:
    """跨链桥接测试"""
    
    def test_create_bridge(self):
        """创建桥接器"""
        bridge = create_bridge('qnt', ['ethereum', 'bsc'])
        assert bridge.chain_id == 'qnt'
        assert 'ethereum' in bridge.supported_chains
    
    def test_create_ticket(self):
        """创建票据"""
        bridge = create_bridge('qnt', ['ethereum'])
        ticket_id = bridge.create_ticket('ethereum', 100.0, 'QNT', '0xUser1')
        
        assert ticket_id is not None
        assert len(ticket_id) == 16
    
    def test_get_ticket_status(self):
        """获取票据状态"""
        bridge = create_bridge('qnt', ['ethereum'])
        ticket_id = bridge.create_ticket('ethereum', 50.0, 'QNT', '0xUser2')
        
        ticket = bridge.get_ticket(ticket_id)
        assert ticket is not None
        assert ticket['amount'] == 50.0
        assert ticket['status'] == 'pending'
    
    def test_invalid_claim(self):
        """无效认领"""
        bridge = create_bridge('qnt', ['ethereum'])
        ticket_id = bridge.create_ticket('ethereum', 10.0, 'QNT', '0xUser3')
        
        # 错误密钥
        result = bridge.claim_ticket(ticket_id, 'wrong_secret')
        assert result == False
    
    def test_get_stats(self):
        """获取统计"""
        bridge = create_bridge('qnt', ['ethereum', 'bsc'])
        bridge.create_ticket('ethereum', 100.0, 'QNT', 'User1')
        bridge.create_ticket('bsc', 50.0, 'ETH', 'User2')
        
        stats = bridge.get_stats()
        assert stats['total_tickets'] == 2
        assert stats['chain_id'] == 'qnt'


class TestAtomicSwap:
    """原子交换测试"""
    
    def test_create_offer(self):
        """创建报价"""
        offer = AtomicSwap.create_offer(
            'qnt', 'ethereum',
            100.0, 0.5,
            'secret123'
        )
        
        assert offer['chain_a'] == 'qnt'
        assert offer['amount_a'] == 100.0
        assert offer['hash_a'] is not None
    
    def test_verify_secret(self):
        """验证密钥"""
        secret = 'my_secret_key'
        hash_expected = AtomicSwap.create_offer('a', 'b', 1, 1, secret)['hash_a']
        
        assert AtomicSwap.verify_secret(secret, hash_expected)
        assert not AtomicSwap.verify_secret('wrong', hash_expected)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
