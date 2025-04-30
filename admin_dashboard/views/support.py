from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from ecommerce.communication.models import CommunicationThread, CommunicationMessage, UploadedFile
from ecommerce.communication.forms import ReplyToThreadForm, StartThreadForm
from django.db.models import Case, When, Value, IntegerField

# List all support tickets
class SupportTicketListView(ListView):
    model = CommunicationThread
    template_name = "admin_dashboard/support/support_list.html"
    context_object_name = "tickets"
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        
        query_set = CommunicationThread.objects.filter(
            type="support_ticket", status__in=['open', 'awiating_admin_reply']
            ).annotate(
                custom_order=Case(
                    When(status='awiating_admin_reply', then=Value(1)),
                    When(status='open', then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField(),
                )
            ).order_by('custom_order', '-created_at')
                    
        
        if search_query:
            query_set = query_set.filter(subject__icontains=search_query)
            
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page', 1)
        tickets = paginator.get_page(page)

        context["tickets_pagination"] = tickets
        context["no_available_data"] = "There are no support tickets available"
        
        context["pagination_info"] = {
            "start": (tickets.start_index() if tickets else 0),
            "end": (tickets.end_index() if tickets else 0),
            "total": paginator.count,
        }
        
        context["search_query"] = self.request.GET.get("q", "")
        
        return context


# View support ticket details
class SupportTicketDetailView(DetailView):
    def get(self, request, pk):
        """Show the support ticket details and appropriate forms."""
        ticket = get_object_or_404(CommunicationThread, pk=pk)
        thread_messages = CommunicationMessage.objects.filter(thread=ticket)

        reply_form = ReplyToThreadForm()
        return render(request, "admin_dashboard/support/ticket_detail.html", {
            "ticket": ticket,
            "thread_messages": thread_messages,
            "reply_form": reply_form,
        })

    def post(self, request, pk):
        """Handle reply to the support ticket."""
        ticket = get_object_or_404(CommunicationThread, pk=pk, type="support_ticket")
        reply_form = ReplyToThreadForm(request.POST)

        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.thread = ticket
            reply.sender = "admin"  # Admin is the sender

            # Handle file uploads
            if request.FILES.getlist('files'):
                for file in request.FILES.getlist('files'):
                    uploaded_file = UploadedFile.objects.create(file=file)
                    reply.files.add(uploaded_file)

            reply.save()
            messages.success(request, "Reply sent successfully.")
        else:
            messages.error(request, "Failed to send reply.")

        return redirect("admin_dashboard:ticket_detail", pk=pk)