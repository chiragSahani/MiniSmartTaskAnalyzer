from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.analyze_tasks import AnalyzeTasksUseCase, SuggestTasksUseCase
from .serializers import TaskInputSerializer, AnalysisResultSerializer

class AnalyzeTasksView(APIView):
    def post(self, request):
        # 1. Validate Input
        serializer = TaskInputSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        tasks_data = serializer.validated_data
        strategy = request.query_params.get('strategy', 'smart_balance')
        
        # 2. Execute Use Case
        use_case = AnalyzeTasksUseCase()
        try:
            results = use_case.execute(tasks_data, strategy_name=strategy)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        # 3. Serialize Output
        output_serializer = AnalysisResultSerializer(results, many=True)
        return Response(output_serializer.data)

class SuggestTasksView(APIView):
    def post(self, request):
        # Using POST to accept a list of tasks to analyze on the fly, 
        # or we could make it GET and read from DB. 
        # Requirement says: "Return the top 3 tasks the user should work on TODAY"
        # It implies it might work on stored tasks, but the analyze endpoint works on input.
        # Let's support both: if body has tasks, use them. If not, use DB.
        
        tasks_data = []
        if request.data:
            serializer = TaskInputSerializer(data=request.data, many=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            tasks_data = serializer.validated_data
        else:
            # Fetch from DB
            from .models import Task
            db_tasks = Task.objects.all()
            # Convert to dicts
            tasks_data = [t.to_dict() for t in db_tasks]

        use_case = SuggestTasksUseCase()
        results = use_case.execute(tasks_data)
        
        output_serializer = AnalysisResultSerializer(results, many=True)
        return Response(output_serializer.data)
