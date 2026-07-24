from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from deposits.models import Deposit
from transfer.models import Transfer
from paiement.models import Payment


class ClientTransactionHistoryView(APIView):
    def get(self, request, client_id):
        deposits = Deposit.objects.filter(wallet__client_id=client_id)
        transfers = (
            Transfer.objects.filter(source_wallet__client_id=client_id)
            | Transfer.objects.filter(destination_wallet__client_id=client_id)
        ).distinct()
        payments = Payment.objects.filter(wallet__client_id=client_id)

        results = []
        for d in deposits:
            results.append({
                'type': 'DEPOSIT', 'id': d.id, 'amount': str(d.amount), 'date': d.created_at,
                'details': {'wallet': d.wallet_id, 'channel': d.channel},
            })
        for t in transfers:
            results.append({
                'type': 'TRANSFER', 'id': t.id, 'amount': str(t.amount), 'date': t.created_at,
                'details': {'source': t.source_wallet_id, 'destination': t.destination_wallet_id},
            })
        for p in payments:
            results.append({
                'type': 'PAYMENT', 'id': p.id, 'amount': str(p.amount), 'date': p.created_at,
                'details': {'wallet': p.wallet_id, 'bill': p.bill_id},
            })

        results.sort(key=lambda x: x['date'], reverse=True)

        txn_type = request.query_params.get('type')
        if txn_type:
            results = [r for r in results if r['type'] == txn_type.upper()]

        return Response(results)


class ClientTransactionStatsView(APIView):
    def get(self, request, client_id):
        total_deposits = Deposit.objects.filter(
            wallet__client_id=client_id
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_transfers = Transfer.objects.filter(
            source_wallet__client_id=client_id
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_payments = Payment.objects.filter(
            wallet__client_id=client_id
        ).aggregate(total=Sum('amount'))['total'] or 0

        count = (
            Deposit.objects.filter(wallet__client_id=client_id).count()
            + Transfer.objects.filter(source_wallet__client_id=client_id).count()
            + Payment.objects.filter(wallet__client_id=client_id).count()
        )

        return Response({
            'total_deposits': total_deposits,
            'total_transfers': total_transfers,
            'total_payments': total_payments,
            'total_transactions': count,
        })