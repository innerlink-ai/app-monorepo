-- Add status column to documents table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'collections' 
        AND table_name = 'documents' 
        AND column_name = 'status'
    ) THEN
        ALTER TABLE collections.documents ADD COLUMN status TEXT;
    END IF;
END $$; 