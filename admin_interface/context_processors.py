def user_details(request):
    if request.user.is_authenticated:
        return {
            'current_user': request.user,
            "current_user_name": request.user.title,
            'is_admin': request.user.is_admin(),
            'is_user': request.user.is_user(),
        }
    return {}