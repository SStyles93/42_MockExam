#include <stdio.h>
#include <stdlib.h>

typedef struct s_list
{
	struct s_list	*next;
	void			*data;
}	t_list;

void	ft_list_foreach(t_list *begin_list, void (*f)(void *));

static void	print_int(void *data)
{
	printf("%d ", *(int *)data);
}

static void	double_int(void *data)
{
	*(int *)data *= 2;
}

int	main(int argc, char **argv)
{
	t_list	*head;
	t_list	*node;
	int		*values;
	int		i;

	values = malloc(sizeof(int) * argc);
	head = NULL;
	i = argc - 1;
	while (i >= 1)
	{
		values[i] = atoi(argv[i]);
		node = malloc(sizeof(t_list));
		node->data = &values[i];
		node->next = head;
		head = node;
		i--;
	}
	ft_list_foreach(head, print_int);
	printf("\n");
	ft_list_foreach(head, double_int);
	ft_list_foreach(head, print_int);
	printf("\n");
	return (0);
}
