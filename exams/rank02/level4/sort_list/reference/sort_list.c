#include "list.h"

t_list	*sort_list(t_list *lst, int (*cmp)(int, int))
{
	t_list	*cur;
	int		tmp;
	int		swapped;

	swapped = 1;
	while (swapped)
	{
		swapped = 0;
		cur = lst;
		while (cur && cur->next)
		{
			if (!cmp(cur->data, cur->next->data))
			{
				tmp = cur->data;
				cur->data = cur->next->data;
				cur->next->data = tmp;
				swapped = 1;
			}
			cur = cur->next;
		}
	}
	return (lst);
}
