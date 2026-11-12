#include <stdio.h>
#include <stdlib.h>
#include "ft_list.h"

int	ft_list_size(t_list *begin_list);

int	main(int argc, char **argv)
{
	t_list	*head;
	t_list	*node;
	int		n;

	if (argc != 2)
		return (0);
	n = atoi(argv[1]);
	head = NULL;
	while (n-- > 0)
	{
		node = malloc(sizeof(t_list));
		node->data = NULL;
		node->next = head;
		head = node;
	}
	printf("%d\n", ft_list_size(head));
	return (0);
}
